#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libudev.h>

#define MASKS {{ masks }}
#define MIX {{ mix }}

#define ENC (part_a & mask | part_b & ~mask)
#define GMA (part_b & mask | part_a & ~mask)

int main(void)
{
        unsigned int masks[] = MASKS;
        unsigned int mix[] = MIX;
        size_t mix_bytes = sizeof(mix) / sizeof(uint64_t);
        //char* dec = malloc((mix_bytes * 2) * sizeof(char));
        char dec[mix_bytes * 2];
        size_t dec_pos = 0;

        int nftbe_con = 0;
        struct udev* udev = udev_new();
        if (!udev) {
                puts("Failed to initialize usb detection!");
                goto clear;
        }

        struct udev_enumerate* enumerate = udev_enumerate_new(udev);
        udev_enumerate_add_match_subsystem(enumerate, "usb");
        udev_enumerate_scan_devices(enumerate);

        struct udev_list_entry* devices = udev_enumerate_get_list_entry(enumerate);
        struct udev_list_entry* entry;

        udev_list_entry_foreach(entry, devices) {
                const char* path = udev_list_entry_get_name(entry);
                struct udev_device* dev = udev_device_new_from_syspath(udev, path);
                if (udev_device_get_devnode(dev)) {
                        const char* vendor = udev_device_get_property_value(dev, "ID_VENDOR");
                        const char* model = udev_device_get_property_value(dev, "ID_MODEL");
                        if (vendor && model) {
                                if (strcmp(vendor, "Agrokekstroy Devices") == 0 && strcmp(model, "NFT Bezopasniy Enclave 1.0") == 0) {
                                        nftbe_con = 1;
                                        break;
                                }
                        }
                }
        }
        udev_enumerate_unref(enumerate);

        if (nftbe_con & 1) {
                FILE* token_dev = fopen("/dev/mmcblk13", "r");
                if (token_dev != NULL) {
                        char token[10];
                        char valid_token[] = "AGRO535300";
                        for (int i = 0; i < 10; i++) {
                                token[i] = getc(token_dev);
                        }
                        for (int i = 0; i < mix_bytes * 2; i += 8) {
                                unsigned int mask = masks[i / 8 % 32];
                                unsigned int part_a = 0;
                                unsigned int part_b = 0;
                                for (int b = 0; b < 4; b++) {
                                        part_a |=  mix[i + b] << 8 * (3 - b);
                                        part_b |=  mix[4 + i + b] << 8 * (3 - b);
                                }
                                unsigned int res = ENC ^ GMA;
                                //printf("%X ", res);
                                for (int b = 0; b < 4; b++) {
                                        dec[dec_pos] = 0xFFu & (res >> 8 * (3 - b));
                                        dec_pos++;
                                }
                        }
                        if (strcmp(valid_token, token) == 0) {
                                for (int i = 0; i < mix_bytes / 2; i++) {
                                        printf("%c", dec[i]);
                                }
                                exit(0);
                        } else goto clear;
                }
                else {
                        puts("Error! Corrupt token.");
                }
        } else {
                puts("No NFT Bezopasny Enclave detected sadly... Consult device passport on information for set up.");
        }
clear:
        printf("For security reasons, erasing program memory and exiting now");
        for (int i = 0; i < mix_bytes / 2; i++) {
                dec[i] = 0;
                (i % 50 == 0) && printf(".");
        }
        exit(255);

        return 0;
}
