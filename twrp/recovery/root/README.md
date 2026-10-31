# Decryption stack for racer (TODO-2) — PLACED 2026-10-31
#
# All 18 files from the verified inventory were pulled (decrypt.tar,
# 1.19 MB) and placed under this directory, mirroring sm84xx-common:
# services in system/bin/ (qseecomd, keymaster@4.0-service-qti,
# gatekeeper@1.0-service-qti), .so libs in vendor/lib64/ and
# vendor/lib64/hw/, .rc files in vendor/etc/init/ with binary paths
# adapted /vendor/bin/hw/* -> /system/bin/* (user/group/class kept
# as the vendor wrote them), device manifest in
# vendor/etc/vintf/manifest.xml (declares keymaster 4.0 + gatekeeper
# 1.0; no keymint HAL — keymint is via the NDK lib).
#
# FOLLOW-UP (small): readelf on the placed files shows 4 transitive
# deps not yet in the tree — pull them the same way (tar to
# /data/local/tmp, then adb pull) and drop them in vendor/lib64/:
#   libdrmfs.so (+ libdrm.so libdrmtime.so libdrmutils.so if present)
#   libqcbor.so
#   android.hardware.security.secureclock-V1-ndk.so (confirmed present)
#   libion.so, only if it exists in /vendor/lib64/
# DONE 2026-10-31: all 7 pulled (decrypt2.tar, 255 KB) and placed.
# readelf on THEM shows one more layer, all small — final round:
#   libdiag.so (libdrmfs.so + libdrmtime.so need it; was in the first
#     inventory, exists), libxml2.so (libdrmfs.so needs it),
#   libtime_genoff.so (libdrmtime.so needs it), libdisplaydebug.so
#   (libdrmutils.so needs it). Pull whichever exist; libdrmtime /
#   libdrmutils themselves are not linked by anything in the set, so
#   their deps are only needed for completeness.
# DONE 2026-10-31: all 4 pulled (decrypt3.tar, 1.42 MB) and placed.
# Full closure re-checked with readelf over every binary/.so in the
# recovery root: 22 vendor .so files, ZERO missing NEEDED libs
# (everything else is a platform lib the recovery image itself
# provides). TODO-2 is fully done.
#
# Key facts the inventory settled (2026-10-31):
#   /vendor/bin/qseecomd
#   /vendor/bin/hw/android.hardware.keymaster@4.0-service-qti
#   /vendor/bin/hw/android.hardware.gatekeeper@1.0-service-qti
#     (name unconfirmed — check `ls /vendor/bin/hw/`)
#   /vendor/lib64/android.hardware.security.keymint-V1-ndk.so
#   /vendor/lib64/android.hardware.keymaster@3.0.so
#   /vendor/lib64/android.hardware.keymaster@4.0.so
#   /vendor/lib64/android.hardware.keymaster@4.1.so
#   /vendor/lib64/android.hardware.gatekeeper@1.0.so
#   /vendor/lib64/libQSEEComAPI.so
#   /vendor/lib64/libkeymasterdeviceutils.so
#   /vendor/lib64/libkeymasterprovision.so
#   /vendor/lib64/libkeymasterutils.so
#   /vendor/lib64/libqtikeymaster4.so
#   /vendor/lib64/hw/android.hardware.gatekeeper@1.0-impl-qti.so
#   /vendor/etc/init/android.hardware.keymaster@4.0-service-qti.rc
#   /vendor/etc/init/android.hardware.gatekeeper@1.0-service-qti.rc
#   /vendor/etc/init/qseecomd.rc
#   /vendor/etc/vintf/manifest.xml (main manifest; check it declares
#     the keymaster HAL — there is NO per-HAL keymaster manifest file)
#   Also confirm whether these two exist (for the _platform symlinks):
#   /vendor/lib64/android.hardware.security.secureclock-V1-ndk.so
#   /vendor/lib64/android.hardware.security.sharedsecret-V1-ndk.so
#
# Key facts the inventory settled:
# - Keymaster service is 4.0 (not 4.1): binary
#   /vendor/bin/hw/android.hardware.keymaster@4.0-service-qti,
#   class early_hal, user system, group system drmrpc. The 4.1 .so
#   exists but there is NO 4.1 service binary and NO keymint service
#   binary at all — keymint is provided via the V1-ndk .so over the
#   keymaster 4.x HAL. BoardConfig.mk's keymint-V1-ndk block matches.
# - There is NO android.hardware.security.keymint-service-qti.rc on
#   the vendor (only the keymaster@4.0 .rc), so garnet's rkp-V3
#   LD_PRELOAD .rc fix does NOT apply to racer — do not copy it.
# - No keymaster impl .so in /vendor/lib64/hw/ (only the gatekeeper
#   one) — the keymaster impl is linked into the service binary.
#
# Then place each file into the matching path under this directory
# (twrp/recovery/root/), mirroring the sm84xx-common layout.
#
# If decryption fails on first boot, the debug order is:
#   1. Does qseecomd start? (logcat in recovery / dmesg)
#   2. Does the keymaster service start and bind?
#   3. Does AERA prompt for the PIN and then unlock /data?
# Each step has its own log line; fix one at a time.
