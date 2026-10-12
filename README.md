# Retro-Go – ESP32-S3 / nano-s3 Fork

This repository is a personal development fork of Retro-Go focused on the **ESP32-S3 DevKitC-1 N16R8** and a small SPI TFT based retro-gaming system.

**Original project:** Retro-Go
**Fork:** `radioman82/retro-go`
**Development branch:** `nano-s3`

This fork contains my hardware-specific adaptations, configuration changes, emulator work and documentation for the ESP32-S3 platform.

> This is a development fork. Not all components described below are finished or fully integrated.

---

## Hardware

### ESP32-S3

Target board:

* ESP32-S3 DevKitC-1
* N16R8
* ESP32-S3
* 16 MB Flash
* 8 MB PSRAM

### ILI9341 SPI TFT

Current display configuration:

| Signal    |   GPIO / Connection |
| --------- | ------------------: |
| CS        | GND (fest auf Masse) |
| MOSI      |              GPIO12 |
| CLK       |              GPIO48 |
| DC        |              GPIO47 |
| RST       |               GPIO3 |
| Backlight |              GPIO39 |

* The **CS** (Chip Select) pin of the ILI9341 display is permanently tied to **GND** (configured as `GPIO_NUM_NC` in code).
* Touch functionality is **not used**.

### SD card

The SD card is connected through SPI:

| Signal |   GPIO |
| ------ | -----: |
| MISO   |  GPIO9 |
| MOSI   | GPIO11 |
| CLK    | GPIO13 |
| CS     | GPIO10 |

The SD card is used for ROMs, disk images and emulator data.

### Audio (MAX98357A I2S DAC)

I2S digital audio output configuration:

| Signal / Pin | ESP32-S3 / Level | Note |
| ------------ | ---------------: | ---- |
| BCLK (BCK)   |           GPIO41 | I2S Bit Clock |
| LRC (WS)     |           GPIO42 | Word Select / Left-Right Clock |
| DIN (DATA)   |           GPIO40 | Serial Data |
| SD           |            3.3 V | Festeingeschaltet (kein Enable-Pin im Code / `GPIO_NUM_NC`) |
| VIN          |      3.3 V / 5 V | Stromversorgung (5 V für 3 W an 4 Ω) |
| GND          |              GND | Masse |

---

## Input

The gamepad button configuration is:

| Function |   GPIO | Configuration |
| -------- | -----: | ------------- |
| UP       |  GPIO6 | Pull-up, Level 0 (Active Low) |
| DOWN     |  GPIO0 | Pull-up, Level 0 (Active Low) |
| LEFT     | GPIO45 | Pull-up, Level 0 (Active Low) |
| RIGHT    |  GPIO7 | Pull-up, Level 0 (Active Low) |
| A        | GPIO15 | Pull-up, Level 0 (Active Low) |
| B        |  GPIO5 | Pull-up, Level 0 (Active Low) |
| SELECT   | GPIO16 | Pull-up, Level 0 (Active Low) |
| START    | GPIO17 | Pull-up, Level 0 (Active Low) |
| MENU     | GPIO18 | Pull-up, Level 0 (Active Low) |
| OPTION   |  GPIO8 | Pull-up, Level 0 (Active Low) |

All buttons are configured with internal pull-ups (`pullup = 1`) and active-low trigger (`level = 0`).

---

## Current Development Status

The ESP32-S3 port is actively being developed.

### Working / tested

* ESP32-S3 DevKitC-1 N16R8 & Waveshare Nano-S3 targets
* Retro-Go builds successfully for ESP32-S3 with ESP-IDF
* ILI9341 & ST7789 SPI displays
* SD card support (SPI)
* ESP32-S3 input/button configuration
* emulator-specific input adaptations
* **Neo Geo Pocket / Neo Geo Pocket Color** core (RACE!) integrated and functional
* **WonderSwan / WonderSwan Color** core (Oswan) integrated and functional
* **MSX / MSX2** core (fMSX) integrated
* **Amiga 500** core (UAE4all / FAME-C) integrated (experimental, see [FAZIT.md](a500/FAZIT.md))
* **PICO-8** core (Fake-08) experimental (sources ported, **not included in current pre-built release image**)
* Firmware images and app partitions generated with `rg_tool.py`

The current ESP32-S3 build system uses **ESP-IDF** rather than the Arduino build system used by some of the earlier experiments.

---

## Emulator Development

Several emulator components have been ported, adapted or integrated on the ESP32-S3.

### SNK Neo Geo Pocket & Neo Geo Pocket Color (RACE!)

* **App Target:** `ngp/`
* **Core Component:** `components/race/`
* **Supported File Types:** `.ngp`, `.ngc`, `.zip`
* **Partition Size:** 896 KB (`ngp` in `rg_tool.py`)
* **Key Implementation Details:**
  * Emulates the Toshiba TLCS-900H 16-bit CPU and Z80 sound co-processor.
  * Native 160×152 rendering scaled into Retro-Go display buffers.
  * **ESP32-S3 Audio Architecture:** Audio message buffers are strictly allocated in internal DRAM (`DRAM_ATTR audio_msg_t audio_pool[...]`) rather than PSRAM to guarantee jitter-free, glitch-free I2S DMA streaming without SPI bus contention.
  * **Universal S3 Sync Formula:** Includes dynamic sample rate compensation to prevent APB/I2S clock drift during CPU frequency adjustments and overclocking.
  * Dedicated FreeRTOS `audio_task` decoupled from the emulation loop via queues.

### Bandai WonderSwan & WonderSwan Color (Oswan)

* **App Target:** `oswan/`
* **Core Component:** `components/oswan/`
* **Supported File Types:** `.ws`, `.wsc`, `.zip`
* **Partition Size:** 640 KB (`oswan` in `rg_tool.py`)
* **Key Implementation Details:**
  * Emulates the NEC V30MZ CPU core (`nec.c`) and custom WonderSwan hardware.
  * Native 224×144 resolution with full monochrome and WonderSwan Color palette rendering (`WSRender.c`).
  * Dedicated input mapping (`ws_input_poll`) supporting X-Pad and Y-Pad button modes mapped seamlessly to standard Retro-Go gamepad controls.
  * WonderSwan Audio Processing Unit (APU) streaming audio directly into Retro-Go's DMA sound queue (`rg_audio_submit`).
  * Save states and EEPROM persistence support (`WSFileio.c`).

### Amiga 500 Development (UAE4all / FAME-C)

* **App Target:** `a500/`
* **Core Component:** `components/a500/`
* **Supported File Types:** `.adf`, `.zip`
* **Partition Size:** 2.0 MB (`a500` in `rg_tool.py`)
* **Status:** Integrated into Retro-Go as an experimental proof-of-concept.
  * Bootable into Kickstart 1.3 (`kick13.rom`), ADF floppy disk loading.
  * Paula 4-channel DMA audio over I2S and 320×240 RGB565 display output.
  * Gamepad joystick mode and selectable mouse mode via `SELECT`.
  * Detailed architectural findings and performance analysis (comparing Musashi vs. UAE4all/FAME-C, PSRAM latency bottlenecks, and frame rates) are documented in [a500/FAZIT.md](a500/FAZIT.md).

### PICO-8 Fantasy Console (Fake-08)

* **App Target:** `fake08/`
* **Core Component:** `fake-08/` (source tree adapted for ESP32-S3)
* **Supported File Types:** `.p8`, `.p8.png`
* **Status:** Integrated into the repository as an **experimental** proof-of-concept (sources ported, but **not included in the current pre-built release build** `v1.04`; under active development).
* **Key Implementation Details:**
  * Uses the Fake-08 emulator engine (`vm.cpp`, `cart.cpp`, `z8lua`).
  * Custom Retro-Go Host integration in `fake08/main/main.cpp` using Retro-Go display buffers (`rg_surface_t`, `rg_display_submit`), audio DMA streaming (`rg_audio_submit`), and input polling.
  * Adapted for Xtensa / ESP-IDF C++ toolchain: fixed 32-bit fixed-point arithmetic (`fix32.h`), `luaconf.h` casting fixes, isolated LodePNG symbol conflicts, and routed console logging directly to standard output.
  * ROMs and cartridges are located at `/sd/roms/pico8`.

---

## Documentation

Additional development documentation is included in:

* `Retro go mit esp32s3 R16N8.docx`: Records early hardware tests and configurations.
* [a500/FAZIT.md](a500/FAZIT.md): Comprehensive evaluation of the Amiga 500 port on ESP32-S3.

---

## Build

The ESP32-S3 targets are built using `rg_tool.py` on top of the ESP-IDF environment.

To build specific emulator binaries:

```bash
# Build Neo Geo Pocket
python rg_tool.py --target esp32-s3-devkit build ngp

# Build WonderSwan
python rg_tool.py --target esp32-s3-devkit build oswan

# Build Fake-08 (PICO-8, experimental)
python rg_tool.py --target esp32-s3-devkit build fake08

# Build all configured applications
python rg_tool.py --target esp32-s3-devkit build
```

Successful builds generate the binaries in each app's `build` directory:

```text
ngp/build/ngp.bin
oswan/build/oswan.bin
fake08/build/fake08.bin
launcher/build/launcher.bin
```

---

## Development Notes

This repository is primarily a development project and should not be considered a finished distribution.

Hardware configuration and emulator support may change as development continues.

The goal is to maintain a documented ESP32-S3 based Retro-Go platform while experimenting with additional emulator support and hardware-specific improvements.

---

## Credits & Upstream Project

This project is an ESP32-S3 port based on the original [Retro-Go by ducalex](https://github.com/ducalex/retro-go).

* **Upstream Repository:** [https://github.com/ducalex/retro-go](https://github.com/ducalex/retro-go)
* **Original Author:** ducalex and contributors
* **Artwork Pack:** [retro-go-covers](https://github.com/ducalex/retro-go-covers)

Please refer to the original repository for upstream documentation and legacy platform support (ODROID-GO, MRGC-G32).

---

## License

Everything in this project is licensed under the [GPLv2 license](COPYING) with the exception of specific emulator cores:
* `fmsx/components/fmsx`: MSX emulator (custom non-commercial license)
* `retro-core/components/handy`: Lynx emulator (zlib)
* `fake-08`: PICO-8 emulator by jtothebell (MIT)
