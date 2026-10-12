#include <rg_system.h>
#include <rg_audio.h>
#include <rg_input.h>
#include <rg_display.h>
#include <rg_surface.h>
#include <rg_gui.h>
#include <esp_heap_caps.h>
#include <stdio.h>
#include <string.h>
#include <string>
#include <vector>

// fake-08 includes
#include "vm.h"
#include "Audio.h"
#include "Input.h"
#include "graphics.h"
#include "host.h"
#include "logger.h"

#define AUDIO_SAMPLE_RATE 22050
#define AUDIO_SAMPLES_PER_FRAME (AUDIO_SAMPLE_RATE / 60)

// Minimal Host implementation for Retro-Go
Host::Host(int windowWidth, int windowHeight) {
    setUpPaletteColors();
}
std::string Host::getCartDirectory() { return "/sd/roms/pico8"; }
std::string Host::customBiosLua() { return ""; }
std::vector<std::string> Host::listcarts() { return std::vector<std::string>(); }
void Host::forceStretch(StretchOption newStretch) {}
InputState_t Host::scanInput() {
    InputState_t state = {0};
    return state;
}
std::vector<std::string> Host::listdirs() { return std::vector<std::string>(); }

class RetroGoHost : public Host {
public:
    RetroGoHost() : Host(128, 128) {}
};

static Vm* p8_vm = nullptr;
static RetroGoHost* p8_host = nullptr;
static uint8_t* p8_ram_pool = nullptr;

static rg_surface_t *updates[2] = {nullptr, nullptr};
static rg_surface_t *currentUpdate = nullptr;
static rg_audio_frame_t audio_buffer[AUDIO_SAMPLES_PER_FRAME + 32];

static void event_handler(int event, void *arg) {
    if (event == RG_EVENT_REDRAW) {
        if (currentUpdate) {
            rg_display_submit(currentUpdate, 0);
        }
    }
}

extern "C" void app_main(void) {
    printf("\n===================================================\n");
    printf("         FAKE-08 (PICO-8) FOR RETRO-GO             \n");
    printf("===================================================\n");

    RG_LOGI("fake08", "Free internal SRAM: %u bytes", (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
    RG_LOGI("fake08", "Free PSRAM:         %u bytes", (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));

    static rg_handlers_t handlers = {
        .event = event_handler,
    };

    rg_app_t *app = rg_system_init(AUDIO_SAMPLE_RATE, &handlers, nullptr);
    if (!app) {
        RG_LOGE("fake08", "rg_system_init failed!");
        return;
    }

    RG_LOGI("fake08", "System initialized. Free SRAM: %u, Free PSRAM: %u",
            (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
            (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));

    // Allocate double-buffered 128x128 surfaces in PSRAM / slow memory
    updates[0] = rg_surface_create(128, 128, RG_PIXEL_565_LE, MEM_SLOW);
    updates[1] = rg_surface_create(128, 128, RG_PIXEL_565_LE, MEM_SLOW);

    if (!updates[0] || !updates[1]) {
        RG_LOGE("fake08", "Failed to allocate display surfaces!");
        rg_gui_alert("Error", "Out of memory for display surfaces");
        rg_system_exit();
        return;
    }
    currentUpdate = updates[0];
    RG_LOGI("fake08", "Display surfaces allocated (128x128 LE).");

    // Allocate 64KB for PicoRam in PSRAM to prevent internal heap starvation
    p8_ram_pool = (uint8_t*)heap_caps_malloc(sizeof(PicoRam), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!p8_ram_pool) {
        RG_LOGW("fake08", "PSRAM allocation for PicoRam failed, trying internal SRAM");
        p8_ram_pool = (uint8_t*)malloc(sizeof(PicoRam));
    }
    if (!p8_ram_pool) {
        RG_LOGE("fake08", "Failed to allocate PicoRam (%u bytes)!", (unsigned)sizeof(PicoRam));
        rg_gui_alert("Error", "Out of memory for PicoRam");
        rg_system_exit();
        return;
    }
    PicoRam* ram = new (p8_ram_pool) PicoRam();

    // Initialize Host and Vm
    p8_host = new RetroGoHost();
    p8_vm = new Vm(p8_host, ram, nullptr, nullptr, nullptr);

    RG_LOGI("fake08", "Core initialization complete.");

    // Validate ROM path
    const char *romPath = app->romPath;
    RG_LOGI("fake08", "ROM path from system: '%s'", romPath ? romPath : "(null)");

    if (!romPath || strlen(romPath) == 0) {
        RG_LOGE("fake08", "No ROM path specified!");
        rg_gui_alert("Pico-8 Error", "No ROM path specified");
        rg_system_exit();
        return;
    }

    FILE *romFile = fopen(romPath, "rb");
    if (!romFile) {
        RG_LOGE("fake08", "Cannot open ROM file at '%s'!", romPath);
        char msg[128];
        snprintf(msg, sizeof(msg), "ROM file not found:\n%.90s", romPath);
        rg_gui_alert("File Not Found", msg);
        rg_system_exit();
        return;
    }
    fseek(romFile, 0, SEEK_END);
    long romSize = ftell(romFile);
    fclose(romFile);
    RG_LOGI("fake08", "ROM file exists, size = %ld bytes", romSize);

    // Load Cartridge
    bool loadSuccess = false;
    try {
        loadSuccess = p8_vm->LoadCart(std::string(romPath));
    } catch (const std::exception& e) {
        RG_LOGE("fake08", "Exception in LoadCart: %s", e.what());
    } catch (...) {
        RG_LOGE("fake08", "Unknown exception in LoadCart!");
    }

    if (!loadSuccess) {
        RG_LOGE("fake08", "Failed to load cart '%s'!", romPath);
        char msg[128];
        snprintf(msg, sizeof(msg), "Failed to load cart:\n%.90s", romPath);
        rg_gui_alert("Cart Load Error", msg);
        rg_system_exit();
        return;
    }

    RG_LOGI("fake08", "Cartridge loaded successfully! Starting main game loop...");

    int frameCount = 0;
    while (!rg_system_exit_called()) {
        rg_system_tick(0);
        uint32_t keys = rg_input_read_gamepad();

        // Map Retro-Go gamepad keys to Pico-8:
        // 0=L, 1=R, 2=U, 3=D, 4=O (B), 5=X (A), 6=Start
        uint8_t p8_input = 0;
        if (keys & RG_KEY_LEFT)   p8_input |= (1 << 0);
        if (keys & RG_KEY_RIGHT)  p8_input |= (1 << 1);
        if (keys & RG_KEY_UP)     p8_input |= (1 << 2);
        if (keys & RG_KEY_DOWN)   p8_input |= (1 << 3);
        if (keys & RG_KEY_B)      p8_input |= (1 << 4); // O button
        if (keys & RG_KEY_A)      p8_input |= (1 << 5); // X button
        if (keys & RG_KEY_START)  p8_input |= (1 << 6); // Start (pause menu)

        p8_vm->getPicoRam()->data[0x5F4C] = p8_input;

        // Step VM frame
        p8_vm->Step();

        // Render Pico-8 128x128 framebuffer to currentUpdate
        uint8_t* fb = p8_vm->GetPicoInteralFb();
        uint8_t* pal = p8_vm->GetScreenPaletteMap();
        Color* colors = p8_host->GetPaletteColors();
        uint16_t* dst = (uint16_t*)currentUpdate->data;

        for (int i = 0; i < 128 * 128; i++) {
            uint8_t c = pal[fb[i] & 0x0F];
            Color rgb = colors[c];
            dst[i] = ((rgb.Red & 0xF8) << 8) | ((rgb.Green & 0xFC) << 3) | (rgb.Blue >> 3);
        }

        rg_display_submit(currentUpdate, 0);
        currentUpdate = (currentUpdate == updates[0]) ? updates[1] : updates[0];

        // Synthesize and submit audio
        p8_vm->FillAudioBuffer((void*)audio_buffer, 0, AUDIO_SAMPLES_PER_FRAME);
        rg_audio_submit(audio_buffer, AUDIO_SAMPLES_PER_FRAME);

        frameCount++;
        if (frameCount % 300 == 0) {
            RG_LOGI("fake08", "Running frame %d | Free SRAM: %u, Free PSRAM: %u",
                    frameCount,
                    (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
                    (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        }
    }

    RG_LOGI("fake08", "Exiting game loop...");

    if (p8_vm) {
        delete p8_vm;
        p8_vm = nullptr;
    }
    if (p8_host) {
        delete p8_host;
        p8_host = nullptr;
    }
    if (p8_ram_pool) {
        heap_caps_free(p8_ram_pool);
        p8_ram_pool = nullptr;
    }
    if (updates[0]) {
        rg_surface_free(updates[0]);
        updates[0] = nullptr;
    }
    if (updates[1]) {
        rg_surface_free(updates[1]);
        updates[1] = nullptr;
    }

    rg_system_exit();
}
