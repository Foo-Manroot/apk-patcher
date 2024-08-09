#!/usr/bin/env python3

import argparse
import re
import zipfile
import requests
import base64

from lzma import decompress, FORMAT_XZ
from shutil import rmtree, move, copy
from pathlib import Path
from io import BytesIO, BufferedReader

from androguard.core.axml import AXMLPrinter
from androguard.core.dex import DEX
from androguard.util import set_log

import pyaxml
try:
    from lxml import etree
    print("[DEBUG] Running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as etree
    print ("[DEBUG] Running with Python's xml.etree.ElementTree")

import jpype
import jpype.imports
# Required before importing the Java classes
jpype.startJVM (classpath = [
    str (Path ("java_libs") / "*"),
    str (Path ("Java") / "APK patcher" / "app" / "build" / "libs" / "*")
])

from java.lang import String, UnsupportedClassVersionError
from java.io import (
    IOException,
    ByteArrayInputStream
)
try:
    from ApkPatcher import Patcher
except UnsupportedClassVersionError as e:
    print (f"[ERROR] {e}")
    print (f"[DEBUG] Using JVM at {jpype.getDefaultJVMPath ()}")
    print (f"(FIX) -> Try to recompile the Java library. See './Java/APK patcher/README.md'")
    print (f"(FIX 2) -> If you have another version of Java installed, try that one instead")
    import sys
    sys.exit (-1)



############
## CONFIG ##
############

GADGET_CONFIG = b"""{
  "interaction": {
    "type": "listen",
    "address": "127.0.0.1",
    "port": 1234,
    "on_port_conflict": "fail",
    "on_load": "resume"
  }
}
"""

FRIDA_ASSETS_URL = "https://api.github.com/repos/frida/frida/releases/latest"

# Android ABI => Frida ABI
# https://developer.android.com/ndk/guides/abis
# https://developer.android.com/ndk/guides/abis.html#native-code-in-app-packages
ABI_MAPPING = {
    "armeabi-v7a": "arm",
    "arm64-v8a": "arm64",
    "x86": "x86",
    "x86_64": "x86_64"
}

# Location of the generated APKs
OUT_DIR = Path.cwd () / "patched_output"

# One could say that it's easier to receive it as a parameter... XD
KEYSTORE_B64 = "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"



def parse_args ():

    parser = argparse.ArgumentParser (
            prog = "APK patcher",
            description = "Script to automate the decompilation, patch and rebuild of any Android split applications (those apps that have base.apk, plus .config.<something>.apk) to inject the provided Frida script.",
            formatter_class = argparse.RawTextHelpFormatter
        )

    parser.add_argument (
            'base_path',
            type = str,
            help = ("Common prefix for all the split apk files.\n"
                    "For example, if we have:\n"
                    "  - com.example.1234.apk\n"
                    "  - com.example.1234.config.armeabi_v7a.apk\n"
                    "  - com.example.1234.config.en.apk\n"
                    "  - com.example.1234.config.xxhdpi.apk\n\n"
                    "'base-name' must be \"com.example.1234.\"\n"
                )
        )

    parser.add_argument (
            'frida_script',
            type = argparse.FileType ("rb"),
            help = "The JS file to patch into the apk."
        )

    args = parser.parse_args ()
    return args


def find_apk_parts (base_name):
    """
    Scans the specified path looking for all the available parts of the split APK.
    Not all parts are mandatory, except for:
        - <base_path>apk
        and
        - <base_path>.config.<arch>.apk

    This second file is also used to select the appropriate Frida gadget to download.
    Note that there might be multiple such files (i.e.: 'test.config.armeabi_v7a.apk' and 'test.config.arm64-v8a.apk'),
    so the returned result will reflect all these .

    Return
        :dict
        The following is a sample returned object:
        {
            "main": "test.apk", // This is the only mandatory item. The other keys may or may not be present
            "abi": [
                "test.config.armeabi_v7a.apk",
                "test.config.arm64_v8a.apk"
            ],
            "density": [
                "test.config.xxhdpi.apk",
                "test.config.ldpi.apk"
            ],
            "lang": [
                "test.config.en.apk",
                "test.config.de.apk"
            ]
        }

    More info: https://developer.android.com/build/configure-apk-splits
    """
    base_path = Path (base_name)

    file_list = base_path.parent.glob (f"{base_path.name}*apk")
    parts = {}

    base = str (base_path.name)

    re_abi = re.compile (f"{base}config\\.(arm|x86)[^.]+\\.apk")
    re_density = re.compile (f"{base}config\\.[a-z]+dpi\\.apk") # https://developer.android.com/training/multiscreen/screendensities
    re_lang = re.compile (f"{base}config\\.[a-z][a-z]\\.apk")

    for f in file_list:

        file = str (f.name)

        if file == f"{base}apk":
            parts ["main"] = f

        elif re_abi.match (file):
            if "abi" in parts:
                parts ["abi"].append (f)
            else:
                parts ["abi"] = [ f ]

        elif re_density.match (file):
            if "density" in parts:
                parts ["density"].append (f)
            else:
                parts ["density"] = [ f ]

        elif re_lang.match (file):
            if "lang" in parts:
                parts ["lang"].append (f)
            else:
                parts ["lang"] = [ f ]

    if "main" not in parts:
        raise FileNotFoundError (f"Couldn't find the main APK (searched for '{base}apk')")

    return parts


def get_entry_points (main_apk_path):
    """
    Unpacks the main APK and parses AndroidManifest.xml to extract the entry points of the app.

    Args
        main_apk_path: str
            Path to the APK containing the AndroidManifest.xml

    Returns
        [:str]
        A list with the names of the classes that were marked as an entry point on the Manifest
    """
    entry_points = []

    with zipfile.ZipFile (main_apk_path, "r") as apk:
        with apk.open ("AndroidManifest.xml") as manifest:
            parsed = AXMLPrinter (manifest.read ())
            xml = parsed.get_xml_obj ()

            # We're looking for any activity wtih action="android.intent.action.MAIN", regardless of its category
            # There might be multiple main activities, depending on how it is launched: https://stackoverflow.com/a/75269947
            main_actions = xml.findall (".//activity/intent-filter/action[@{http://schemas.android.com/apk/res/android}name='android.intent.action.MAIN']")

            for action in main_actions:
                # We expect the following hierarchy:
                #  <activity android:theme=...>
                #  <intent-filter>
                #    <action android:name="android.intent.action.MAIN"/>
                #    <category android:name="android.intent.category.LAUNCHER"/>
                #    <action android:name="android.intent.action.VIEW"/>
                #  </intent-filter>
                activity = action.getparent ().getparent ()
                name = activity.get ("{http://schemas.android.com/apk/res/android}name")

                if name not in entry_points:
                    entry_points.append (name)

    return entry_points


#def gen_patch_stub (dex, method):
#    """
#    Generates the stub to load "libgadget.so"
#
#    Args:
#        dex :androguard.core.dex.DEX
#            Reference to the DEX where the given method was defined.
#            Needed to fix the string/method references.
#
#        method :androguard.core.dex.EncodedMethod
#            Method where the stub is going to be prepended
#
#    Returns:
#        [:androguard.core.dex.Instruction]
#        A list with the DEX instructions
#    """
#    # https://source.android.com/docs/core/runtime/dalvik-bytecode
#    # http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html
#    # https://github.com/androguard/androguard/blob/master/androguard/core/dex/__init__.py
#
#    class_mgr = dex.get_class_manager ()
#    n_registers = method.code.get_registers_size ()
##    n_strings = dex.get_len_strings ()
##
##    print ("==============")
##    print (f"n_strings before: {dex.get_len_strings ()}")
##
##    #dex.strings.append (
##    #        StringDataItem (
##    #                # Null-terminated for the DEX class to interpret it correctly, or smth (?)
##    #                # idk, it hangs otherwise:
##    #                #   Traceback (most recent call last):
##    #                # File "...\androguard\core\dex\__init__.py", line 1991, in __init__
##    #                #    self.data = read_null_terminated_string(buff)
##    #                #                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
##    #                #  File "...\androguard\core\dex\__init__.py", line 108, in read_null_terminated_string
##    #                #    while True:
##    #                #          ^^^^
##    #                BytesIO (b"gadget\x00"),
##    #                class_mgr
##    #            )
##    #    )
##
##    mi = MapItem (
##            BytesIO (
##                    # Little endian !!!
##                    b"\x02\x20" + # Type // https://source.android.com/docs/core/runtime/dex-format#type-codes
##                    b"\x01\x23" + # unused (?)
##                    b"\x01\x00\x00\x00" + # size
##                    b"\x00\x00\x00\x00" + # Offset (start of the string, or smth)
##                    b"gadget\x00"
##                ),
##            class_mgr
##        )
##    mi.parse ()
##    class_mgr.add_type_item (
##            mi.get_type (),
##            mi,
##            list (mi.get_item ())
##        )
##    #class_mgr.set_hook_string (n_strings, "gadget")
##    print (len (dex.strings))
##
##    print (f"n_strings after: {dex.get_len_strings ()}")
##
##    i = -1
##    s = ""
##    while s != "AG:IS: invalid string":
##        i += 1
##        s = class_mgr.get_string (i)
##
##    print (f"cm string@[{i-1}]: {class_mgr.get_string (i-1)}")
#
##    load_lib = dex.get_classes_def_item ().get_method ("Ljava/lang/System;", "loadLibrary")
##
##    if load_lib:
##        load_lib = load_lib[0]
##    else:
##        # loadLibrary() was not found in the current DEX
##        load_lib = dex.get_classes_def_item ().get_method ("Lch/admin/swisstopo/SwisstopoApplication;", "onCreate")[0]
##        print (load_lib)
##        instructions = list (load_lib.get_instructions ())
##
##        ####
##        for ins in instructions:
##            print(ins.get_op_value(), ins.get_name(), ins.get_output(), ins.get_hex())
##
##        for s in dex.get_string_data_item ():
##            if "swisstopo_app_shared" in s.get ():
##                s.show ()
##                print (s.get_off ())
##
##        load_lib = dex.get_class_manager ().get_method_ref (0x8c2f)
##        load_lib.show ()
#
#    # I didn't find any other way to access the external method declarations
#    # loadLibrary() is part of the Android API, so it will not appear in the methods defined by the APK.
#    # Instead, just a string will be used to reference it (or smth, idk?)
#    method_ref_idx = None
#
#    methods = dex.get_class_manager ()._ClassManager__manage_item[TypeMapItem.METHOD_ID_ITEM]
#
#    for i, m in enumerate (methods.gets ()):
#        if m.get_name () == "loadLibrary" \
#        and m.get_class_name () == "Ljava/lang/System;":
#            print (f"[INFO] Found loadLibrary at index {i}")
#            m.show ()
#            method_ref_idx = i
#
#    if not method_ref_idx:
#        # TODO: add `System.loadLibrary()` import
#        raise IndexError ("Couldn't find java.lang.System.loadLibrary() on the existing imports")
#
##    print ("//////////////")
#
#    return [
#        Instruction21c (class_mgr,
#                # const-string vXX, "gadget"
#                pack ("B", 0x1a) + # Opcode
#                pack ("B", n_registers % 0xFF) + # destination register (8 bits)
#                pack ("<H", 44339) # string index (44339 => "zoomToTrack")
#            ),
#        Instruction35c (class_mgr,
#                # invoke-static {vXX}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
#                pack ("B", 0x71) + # Opcode
#                pack ("B", 0x1 << 4) + # Arg count (4 bits)
#                pack ("<H", method_ref_idx) + # method reference (16 bits)
#                pack ("<H", n_registers % 0xFF) # Arg register (4 bits each)
#            )
#    ]


def java_patch_bytecode (dex_raw_bytes, dex_version, main_class, init_method):
    """
    Interfaces with the custom patcher written in Java, which uses the dexlib2 library.
    This is needed because androguard doesn't support modifying the dex files, as far as I could tell
    """
    output = None
    class_name = main_class.name
    method_name = init_method.name

    print (f"[DEBUG] Interfacing with the Java patcher to modify {class_name}->{method_name}" +
        f"// Dex version: {dex_version}")

    j_dexBytes = ByteArrayInputStream (dex_raw_bytes)
    j_className = String (class_name)
    j_methodName = String (method_name)
    j_dexVersion = dex_version # Basic type; no conversion is needed. This variable is for better code readability

    try:
        j_output = Patcher.patchDexFile (j_dexBytes, j_className, j_methodName, j_dexVersion)

        output = bytes (j_output.toByteArray ())

    except IOException as e:
        print (f"[ERROR] Exception from Java at patchDexFile(): {e} ")

    return output


def get_init_method (main_class):
    # https://source.android.com/docs/core/runtime/dex-format#access-flags
    # 0x10000 -> constructor
    # If there are many constructors, we just take the first one (although we could patch all of them, just in case...)
    init_method = list (
            filter (
                    lambda x: x.access_flags & 0x10000,
                    main_class.get_methods ()
                )
        )[0]

#    # I have no clue what the difference between <clinit> and <init> is, so we just take the first one found and roll with it
#    # In any case, at least one of the two must always exist (afaik...)
#    init_method = list (
#            filter (
#                    lambda x: x.get_name () == "<clinit>" or x.get_name () == "<init>",
#                    main_class.get_methods ()
#                )
#        )[0]

    return init_method


def copy_to_zip (handle_zip_original, handle_zip_new, filename, data = None):
    """
    Copies the filename from zip_original to zip_new.
    If "data" is provided, those bytes are copied instead of the original file data.

    Args
        handle_zip_original: ZipFile
            Handle to the original zipfile from where to copy the data.

        handle_zip_new: ZipFile
            Handle to the new zipfile, where the data will be copied to.

        filename: str
            Path to the file that will be copied.

        data: bytes
            Data to be put into the new zip, instead of the original file's data.
            The original file's metadata is kept.
    """
    # The metadata is kept regardless of the data we copy
    info = handle_zip_original.getinfo (filename)

    if data is None:
        with handle_zip_original.open (filename) as zipped_file:
            handle_zip_new.writestr (info, zipped_file.read ())

    else:
        handle_zip_new.writestr (info, data)


def patch_bytecode (main_apk_path, mod_apk_path, target_classes):
    """
    Finds the specified class withing the main APK and patches its Bytecode to load the library "libgadget.so"

    Args
        main_apk_path: str
            Path to the APK containing the AndroidManifest.xml

        mod_apk_path: str
            Path to the modified APK where the patched items will be written to

        target_class: [str]
            FQN of the classes to patch, as extracted by get_entry_points()

    Returns
        :bool
        True on success, False otherwise
    """
    with (
        zipfile.ZipFile (main_apk_path, "r") as apk,
        zipfile.ZipFile (mod_apk_path, "w") as apk_mod
    ):
#        dex_list = list (
#                filter (
#                        lambda x: x.endswith (".dex"),
#                        apk.namelist ()
#                    )
#            )

#        for dex_file in dex_list:
        for filename in apk.namelist ():

            if filename.endswith (".dex"):

                dex_bytes = apk.open (filename, "r").read ()
                print (f"[INFO] Parsing {filename}...")
                data = DEX (dex_bytes)

                for t in target_classes:
                    # There might be multiple subclasses (i.e.: Main, Main$a, Main$b, ...), but the entry_point is the
                    # parent one, so we have to search only for "Main;", hence the regex "{t};"
                    main_class = list (
                            filter (
                                    lambda x: re.search (f"{t};", x.get_name ()),
                                    data.get_classes ()
                                )
                        )

                    if (not main_class) or (len (main_class) <= 0):
                        # Not the droids we're looking for... Just add them to the output APK
                        copy_to_zip (apk, apk_mod, filename)
                        continue

                    # If there are more than one element (is that even possible?), we just take the first one
                    main_class = main_class [0]

                    init_method = get_init_method (main_class)
                    print (f"[INFO] Found init method: {init_method}")

                    patched_dex = java_patch_bytecode (dex_bytes, data.version, main_class, init_method)

                    if not patched_dex:
                        print ("[ERROR] Couldn't patch the desired method")
                        continue

                    copy_to_zip (apk, apk_mod, filename, patched_dex)

            else:
                copy_to_zip (apk, apk_mod, filename)

#                instructions = gen_patch_stub (data, init_method) \
#                            + list (init_method.get_instructions ())
#
#                init_method.set_instructions (instructions)
#                init_method.reload ()
#
#                print ("[INFO] Patched method:")
#                init_method.show ()
#
#                print ("[INFO] Saving patched DEX")
#                data._flush ()
#                new_data = data.save ()
#                with open (f"{dex_file}.MODIFIED", "wb") as f:
#                    written = f.write (new_data)
#                    if written > 0:
#                        print (f"[INFO] Wrote {written} Bytes into '{dex_file}.MODIFIED' successfully")
#                    else:
#                        print (f"[ERROR] Couldn't write modified DEX file")

                ####
#                for ins in instructions:
#                    print(ins.get_op_value(), ins.get_name(), ins.get_output(), ins.get_hex())
#                return False
                ####

    return True


def get_arch_from_filename (filename):
    """
    Deducts the required architecture(s) from the file name.
    If no arch could be deduced, then all possibilities are returned.

    The expected file name is: com.test.config.<ABI>.apk
    """
    # Thanks to Pathlib.stem, we can just take out the .apk extension
    # and then get the '<ABI>' part using .stem.split (".")[-1]
    # This way, no index checking has to be performed ([-1] always exists)
    abi = filename.stem.split (".")[-1]
    all_arch = [ ABI_MAPPING[x] for x in ABI_MAPPING ]

    print (f"[DEBUG] Deducted ABI from file {filename}: {abi}")

    # Filenames do not have '-', but use '_'
    abi = abi.replace ("_", "-")
    if not abi in ABI_MAPPING:
        print (f"[DEBUG] Failed to find {abi} within the ABI_MAPPING: {ABI_MAPPING}")
        return all_arch

    return [ ABI_MAPPING [abi] ]


def arch_to_dirname (arch):
    """
    Converts the given arch to the dirname expected inside an APK.
    If the requested architecture was not found, this method returns None
    """
    for abi in ABI_MAPPING:
        if ABI_MAPPING [abi] == arch:
            return abi

    return None


def add_native_lib_to_apk (apk_path, out_path, frida_script):
    """
    Downloads the Frida gadget and adds it to the APK, generating a copy of it.
    The original APK is not modified.
    """
    architectures = get_arch_from_filename (apk_path)

    print (f"[INFO] Requesting {FRIDA_ASSETS_URL}")
    r = requests.get (FRIDA_ASSETS_URL)
    if r.status_code != 200:
        print (f"[ERROR] Couldn't GET {FRIDA_ASSETS_URL} . Response code: {r.status_code} {r.reason}")
        return

    frida_releases = r.json ()
    frida_version = frida_releases ["tag_name"]
    print (f"[INFO] Using Frida version {frida_version} (latest)")

    frida_assets = frida_releases ["assets"]

    with (
        zipfile.ZipFile (apk_path, "r") as in_apk,
        zipfile.ZipFile (out_path, "a") as out_apk
    ):

        # First we add all the original files to the new APK
        for filename in in_apk.namelist ():
            copy_to_zip (in_apk, out_apk, filename)

        # Then, the new items
        for arch in architectures:
            print (f"[INFO] Processing architecture {arch}")

            target = f"frida-gadget-{frida_version}-android-{arch}.so.xz"

            for asset in frida_assets:
                if asset ["name"] == target:
                    download_url = asset ["browser_download_url"]
                    print (f"[INFO] Located {target} @ {download_url}")

                    with requests.get (download_url, stream = True) as r:
                        if r.status_code != 200:
                            print (f"[ERROR] Couldn't GET {FRIDA_ASSETS_URL} . Response code: {r.status_code} {r.reason}")
                            continue

                        lib_xz = r.content
                        lib = decompress (lib_xz, format = FORMAT_XZ)
                        dirname = arch_to_dirname (arch)

                        if dirname is None:
                            # idk, man...
                            dirname = arch

                        out_apk.writestr (f"lib/{dirname}/libgadget.so", lib)
                        out_apk.writestr (f"lib/{dirname}/libgadget.config.so", GADGET_CONFIG)
                        out_apk.writestr (f"lib/{dirname}/libgadget.js.so", frida_script)
                        print (f"[DEBUG] Added all *.so to {out_path}!lib/{dirname}/")


def get_full_filelist (parts, use_basename = False):
    """
    Given a dictionary generated by `find_apk_parts()`, gets all the filenames of each part and
    returns them as a list.

    The argument `use_basename` controls whether the full Path (as an object) or the file basename (as a string)
    should be included in the list.

    Expected input format:
        {
            "main": "test.apk", // This is the only mandatory item. The other keys may or may not be present
            "abi": [
                "test.config.armeabi_v7a.apk",
                "test.config.arm64_v8a.apk"
            ],
            "density": [
                "test.config.xxhdpi.apk",
                "test.config.ldpi.apk"
            ],
            "lang": [
                "test.config.en.apk",
                "test.config.de.apk"
            ]
        }
    """
    files = []

    # If "main" is not there, something is very wrong. I'll let that fail
    files.append (parts ["main"].name if use_basename else parts ["main"])

    for k in [ "abi", "density", "lang" ]:
        if k in parts:
            if use_basename:
                for p in parts [k]:
                    files.append (p.name)
            else:
                files += parts [k]

    return files


def permission_exists (manifest_xml, permission_name):
    """
    Iterates through the provided XML object (lxml.etree.Element or xml.etree.ElementTree) and returns:
        - True if the given permission name exists (verbatim); or
        - False otherwise.
    """

    ret_val = False
    # We're looking for something like this:
    # <uses-permission android:name="android.permission.INTERNET" />
    android_name = "{http://schemas.android.com/apk/res/android}name"

    for permission in manifest_xml.findall ("uses-permission"):
        if permission.attrib [android_name] == permission_name:
            ret_val = True

    return ret_val



def add_permission (manifest_xml, permission_name):
    """
    Adds the specified permission to the given XML object (lxml.etree.Element or xml.etree.ElementTree), which is
    expected to have the AndroidManifest.xml format (i.e.: the element "manifest" must at be the root).

    The permission name must be the full one (i.e.: "android.permission.INTERNET", not just "INTERNET")
    """
    android_name = "{http://schemas.android.com/apk/res/android}name"

#    for i in range (len (manifest_xml)):
#
#        if manifest_xml[i].tag == 'application' or manifest_xml[i].tag == 'uses-permission':
#            new_perm = etree.Element ("uses-permission")
#            new_perm.attrib [android_name] = permission_name
#
#            manifest_xml.insert (i, new_perm)
#            break

    new_perm = etree.Element ("uses-permission")
    new_perm.attrib [android_name] = permission_name

    # https://developer.android.com/guide/topics/manifest/uses-permission-element
    # <uses-permission> is contained within <manifest>, which is the (assumed) root
    # of manifest_xml
    manifest_xml.append (new_perm)


def set_extract_native_libs (manifest_xml):
    """
    Parses the given XML object (lxml.etree.Element or xml.etree.ElementTree), which is
    expected to have the AndroidManifest.xml format (i.e.: the element "application" must exist), and
    sets the attribute `android:extractNativeLibs` to True, if it's not already set.
    """
    android_extractNativeLibs = "{http://schemas.android.com/apk/res/android}extractNativeLibs"

    for app in manifest_xml.findall ("application"):
        if not app.attrib [android_extractNativeLibs] \
            or app.attrib [android_extractNativeLibs] == "false":

            print ("[DEBUG] android:extractNativeLibs was set to false. Patching...")
            app.attrib [android_extractNativeLibs] = "true"



def fix_manifest (apk_path, out_path):
    """
    Modifies the AndroidManifest.xml and packs it into out_path.
    The following items are modified:
        - Add `<uses-permission android:name="android.permission.INTERNET" />`, if not already present
        - Add `extractNativeLibs=true`, if not already present
    """

    with (
        zipfile.ZipFile (apk_path, "r") as in_apk,
        zipfile.ZipFile (out_path, "a") as out_apk
    ):
        for filename in in_apk.namelist ():
            if filename != "AndroidManifest.xml":
                copy_to_zip (in_apk, out_apk, filename)
                continue

            with in_apk.open (filename) as f:
                axml, _ = pyaxml.AXML.from_axml (f.read ())
                xml = axml.to_xml ()

                inet_perm = "android.permission.INTERNET"
                if not permission_exists (xml, inet_perm):
                    print (f"[DEBUG] No {inet_perm} permission.")
                    print ("[WARNING] It's possible that the gadget has no internet connectivity. Check `logcat` for messages like `Frida   : Failed to start: Unable to create socket: Operation not permitted`")
                    # FIXME
 #                   add_permission (xml, inet_perm)
                else:
                    print (f"[DEBUG] App has {inet_perm} permission.")

                set_extract_native_libs (xml)
#                print (etree.tostring (xml, pretty_print = True).decode ("utf-8"))

                reencoded_axml = pyaxml.axml.AXML ()
                reencoded_axml.from_xml (xml)

#                asdf, _ = pyaxml.AXML.from_axml (reencoded_axml.pack ())
#                print ("============================")
#                print (etree.tostring (asdf.to_xml (), pretty_print = True).decode ("utf-8"))

            #################
            # FIXME: seems to break the resulting AXML:
            # $ aapt2 d xmltree --file AndroidManifest.xml patched_output/app-debug.apk
            # ResourceType W 08-09 11:26:14 25258 25258] XML size 0x856 or headerSize 0x1c is not on an integer boundary.
            # patched_output/app-debug.apk: error: failed to parse binary AndroidManifest.xml: failed to initialize ResXMLTree.
            #
            # For the moment, the original manifest ( `copy_to_zip (in_apk, out_apk, filename) ` ) is preserved
            #################

            info = in_apk.getinfo (filename)
            out_apk.writestr (info, reencoded_axml.pack ())
#            print ("[WARNING][FIXME] Patching of the AndroidManifest.xml tends to fail. Discarding patch...")
#            copy_to_zip (in_apk, out_apk, filename)


if __name__ == "__main__":
    set_log ("ERROR") # Androguard logger
    args = parse_args ()

    ####
    # Preparation of the environment
    keystore_data = base64.b64decode (KEYSTORE_B64)
    # The patched items will be written to a modified version inside OUT_DIR
    rmtree (OUT_DIR, ignore_errors = True)
    OUT_DIR.mkdir (parents = True)

    print (f"[INFO] Using {OUT_DIR} as working directory.")
    ####

    # 1: Locate all files that belong to this app
    parts = find_apk_parts (args.base_path)
    print (f"[INFO] Found parts: {get_full_filelist (parts, True)}")

    main_apk_path = parts ["main"]
    mod_apk_path = OUT_DIR / main_apk_path.name

    # 2: Find the entry point(s)
    entry_points = get_entry_points (main_apk_path)

    print (f"[INFO] Found entry point(s): {entry_points}")

    # 3: Patch the entrypoints' Bytecode
    patch_bytecode (main_apk_path, mod_apk_path, entry_points)

    # 4: Download Frida and add it to the lib/ directory

    frida_script = args.frida_script.read ()

    if "abi" in parts:

        for path in parts ["abi"]:
            out_path = OUT_DIR / path.name
            add_native_lib_to_apk (path, out_path, frida_script)

    else:
        # Support for single APKs (or APKs without native libs)
        tmp_mod = mod_apk_path.with_suffix (".tmp")
        add_native_lib_to_apk (mod_apk_path, tmp_mod, frida_script)
        move (tmp_mod, mod_apk_path)

    # 5: Add extractNativeLibs=true to the AndroidManifest.xml, to
    # extract the config
    # Also, android.permission.INTERNET has to be added to allow the Gadget to open
    # a socket (assuming that was the config)
    tmp_mod = mod_apk_path.with_suffix (".tmp")
    fix_manifest (mod_apk_path, tmp_mod)
    move (tmp_mod, mod_apk_path)

    # 6: copy everything (even the items we haven't modified) to OUT_DIR
    files = get_full_filelist (parts)

    for f in files:
        out_path = OUT_DIR / f.name
        print (f"[DEBUG] Processing {out_path}")

        if not out_path.exists ():
            print (f"[DEBUG] Copying unmodified file: {f}")
            copy (f, out_path)

    # 7: zipalign everything
        print (f"[DEBUG] Zipaligning...")
        Patcher.zipAlign (str (out_path))

    # 8: sign everything
        # We have to sign all parts with the same key, regardless of whether
        # we modified them or not
        print (f"[DEBUG] Signing...")
        tmp_file = str (Patcher.signApk (str (out_path), keystore_data))
        move (tmp_file, out_path)

    print (f"[+] All done! The output APK can be found at {OUT_DIR}")
