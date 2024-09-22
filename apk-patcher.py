#!/usr/bin/env python3

import argparse
import re
import zipfile
import requests
import base64
from sys import exit as sys_exit
from sys import stdout

from lzma import decompress, FORMAT_XZ
from shutil import rmtree, move, copy
from pathlib import Path
from io import BytesIO, BufferedReader

from androguard.core.axml import AXMLPrinter
from androguard.core.dex import DEX
from androguard.util import set_log

from loguru import logger

import pyaxml
try:
    from lxml import etree
#    logger.debug ("[DEBUG] Running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as etree
#    logger.debug ("[DEBUG] Running with Python's xml.etree.ElementTree")

import jpype
import jpype.imports
# Required before importing the Java classes
jpype.startJVM (classpath = [
    str (Path (__file__).parent / "java_libs" / "*"),
    str (Path (__file__).parent / "Java" / "APK patcher" / "app" / "build" / "libs" / "*")
])

from java.lang import String, UnsupportedClassVersionError
from java.io import (
    IOException,
    ByteArrayInputStream
)
try:
    from ApkPatcher import Patcher
except UnsupportedClassVersionError as e:
    logger.critical (f"{e}")
    logger.debug (f"Using JVM at {jpype.getDefaultJVMPath ()}")
    logger.error (f"(FIX) -> Try to recompile the Java library. See './Java/APK patcher/README.md'")
    logger.error (f"(FIX 2) -> If you have another version of Java installed, try that one instead")
    sys_exit (-1)



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

# Location of the generated APKs (the app stem will be appended later in __main__)
OUT_DIR = Path.cwd ()

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
                    "'base-name' must be \"com.example.1234.\" (note the dot at the end)\n"
                )
        )

    parser.add_argument (
            '-f', '--fix_manifest',
            action = "store_true",
            help = (
                "If set, the script will attempt to modify AndroidManifest.xml to set extractNativeLibs=true.\n"
                "ATTENTION: it may cause problems like 'INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION' on installation."
            )
        )

    parser.add_argument (
            '-c', '--config',
            dest = "gadget_config",
            type = argparse.FileType ("r"),
            help = "Path to a custom Gadget config ( https://frida.re/docs/gadget/ )"
        )

    parser.add_argument (
            '-v', '--verbose',
            action = "count",
            default = 0,
            help = "Increase the verbosity. Can be specified up to 3 times."
        )

    parser.add_argument (
            '-l', '--load',
            metavar = 'frida_script',
            dest = "frida_script",
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

            android_name = "{http://schemas.android.com/apk/res/android}name"
            android_target = "{http://schemas.android.com/apk/res/android}targetActivity"
            # We're looking for any activity (or activity-alias) wtih action="android.intent.action.MAIN", regardless of its category
            # There might be multiple main activities, depending on how it is launched: https://stackoverflow.com/a/75269947
            #
            # We expect the following hierarchy:
            #  <activity android:theme=...>
            #    <intent-filter>
            #      <action android:name="android.intent.action.MAIN"/>
            #      <category android:name="android.intent.category.LAUNCHER"/>
            #      <action android:name="android.intent.action.VIEW"/>
            #    </intent-filter>
            #  </activity>
            #
            # Therefore, and since Python's default XML parser doesn't support .getparent(), the XPath must go directly to the parent
            # using '/..' (looks like Python libraries don't support '/parent::*' )
            xpath = f".//activity/intent-filter/action[@{android_name}='android.intent.action.MAIN']/../.."
            logger.debug (f'Searching for the entry point using the following XPath: `{xpath}`')
            main_activities = xml.findall (xpath)

            # If none was found, maybe the activity was defined as an 'activity-alias':
            #   <activity-alias
            #           android:name="com.example.LoginActivity"
            #           android:targetActivity="com.example.LaunchActivity">
            # The actual code will be inside com.example.LaunchActivity
            #
            # https://developer.android.com/guide/topics/manifest/activity-alias-element
            search_alias = not main_activities
            if search_alias:
                xpath = f".//activity-alias/intent-filter/action[@{android_name}='android.intent.action.MAIN']/../.."

                logger.debug ("No main activity was found using the previous filter. Trying with <activity-alias>...")
                main_activities = xml.findall (xpath)

            # Python libraries also don't seem to support '/@attrib' to get the attribute directly, so I guess we'll have to do it by hand...
            for activity in main_activities:
                name = activity.get (android_target if search_alias else android_name)

                if name not in entry_points:
                    entry_points.append (name)

    return entry_points


def java_patch_bytecode (dex_raw_bytes, dex_version, main_class, init_method):
    """
    Interfaces with the custom patcher written in Java, which uses the dexlib2 library.
    This is needed because androguard doesn't support modifying the dex files, as far as I could tell
    """
    output = None
    class_name = main_class.name
    method_name = init_method.name

    logger.debug (f"Interfacing with the Java patcher to modify {class_name}->{method_name}" +
        f"// Dex version: {dex_version}")

    j_dexBytes = ByteArrayInputStream (dex_raw_bytes)
    j_className = String (class_name)
    j_methodName = String (method_name)
    j_dexVersion = dex_version # Basic type; no conversion is needed. This variable is for better code readability

    try:
        j_output = Patcher.patchDexFile (j_dexBytes, j_className, j_methodName, j_dexVersion)

        output = bytes (j_output.toByteArray ())

    except IOException as e:
        logger.error (f"Exception from Java at patchDexFile(): {e} ")

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
        done = False
        for filename in apk.namelist ():

            if (not done) and filename.endswith (".dex"):

                dex_bytes = apk.open (filename, "r").read ()
                logger.info (f"Parsing {filename}...")
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

                    if not main_class:
                        # Not the droids we're looking for... Just add them to the output APK
                        copy_to_zip (apk, apk_mod, filename)
                        continue

                    # If there are more than one element (is that even possible?), we just take the first one
                    main_class = main_class [0]

                    init_method = get_init_method (main_class)
                    logger.info (f"Found init method: {init_method}")

                    patched_dex = java_patch_bytecode (dex_bytes, data.version, main_class, init_method)

                    if not patched_dex:
                        logger.error ("Couldn't patch the desired method")
                        return False

                    copy_to_zip (apk, apk_mod, filename, patched_dex)
                    done = True

            else:
                copy_to_zip (apk, apk_mod, filename)


    return done


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

    logger.debug (f"Deducted ABI from file {filename}: {abi}")

    # Filenames do not have '-', but use '_'
    abi = abi.replace ("_", "-")
    if not abi in ABI_MAPPING:
        logger.debug (f"Failed to find {abi} within the ABI_MAPPING: {ABI_MAPPING}")
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


def add_native_lib_to_apk (apk_path, out_path, frida_script = None, gadget_config = None):
    """
    Downloads the Frida gadget and adds it to the APK, generating a copy of it.
    The original APK is not modified.
    """
    architectures = get_arch_from_filename (apk_path)

    logger.info (f"Requesting {FRIDA_ASSETS_URL}")
    r = requests.get (FRIDA_ASSETS_URL)
    if r.status_code != 200:
        logger.error (f"Couldn't GET {FRIDA_ASSETS_URL} . Response code: {r.status_code} {r.reason}")
        return

    frida_releases = r.json ()
    frida_version = frida_releases ["tag_name"]
    logger.info (f"Using Frida version {frida_version} (latest)")

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
            logger.info (f"Processing architecture {arch}")

            target = f"frida-gadget-{frida_version}-android-{arch}.so.xz"

            for asset in frida_assets:
                if asset ["name"] == target:
                    download_url = asset ["browser_download_url"]
                    logger.info (f"Located {target} @ {download_url}")

                    with requests.get (download_url, stream = True) as r:
                        if r.status_code != 200:
                            logger.info (f"Couldn't GET {FRIDA_ASSETS_URL} . Response code: {r.status_code} {r.reason}")
                            continue

                        lib_xz = r.content
                        lib = decompress (lib_xz, format = FORMAT_XZ)
                        dirname = arch_to_dirname (arch)

                        if dirname is None:
                            # idk, man...
                            dirname = arch

                        out_apk.writestr (f"lib/{dirname}/libgadget.so", lib)
                        if gadget_config:
                            out_apk.writestr (f"lib/{dirname}/libgadget.config.so", gadget_config)
                        if frida_script:
                            out_apk.writestr (f"lib/{dirname}/libgadget.js.so", frida_script)
                        logger.debug (f"Added all *.so to {out_path}!lib/{dirname}/")


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

            logger.debug ("android:extractNativeLibs was set to false. Patching...")
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
                    logger.debug (f"No {inet_perm} permission.")
                    logger.warning ("It's possible that the gadget has no internet connectivity. Check `logcat` for messages like `Frida: Failed to start: Unable to create socket: Operation not permitted`")
                    # FIXME
 #                   add_permission (xml, inet_perm)
                else:
                    logger.debug (f"App has {inet_perm} permission.")

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
            copy_to_zip (in_apk, out_apk, filename, reencoded_axml.pack ())
#            logger.warning ("[FIXME] Patching of the AndroidManifest.xml tends to fail. Discarding patch...")
#            copy_to_zip (in_apk, out_apk, filename)


if __name__ == "__main__":

    args = parse_args ()
    OUT_DIR = OUT_DIR / (args.base_path + "patched")

    verbosity = args.verbose
    levels = [ "SUCCESS", "INFO", "DEBUG", "TRACE" ]
    log_level = min ( len (levels) - 1, verbosity )

    logger.remove () # Removes the Androguard logger
    logger.add (
        stdout,
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level:<8}</level> | <level>{message}</level>",
        filter = __name__,
        level = levels [log_level],
        colorize = True
    )

    logger.info (f"Set debugging level to {levels [log_level]}")

    ####
    # Preparation of the environment
    keystore_data = base64.b64decode (KEYSTORE_B64)
    # The patched items will be written to a modified version inside OUT_DIR
    rmtree (OUT_DIR, ignore_errors = True)
    OUT_DIR.mkdir (parents = True)

    logger.info (f"Using {OUT_DIR} as working directory.")
    ####

    # 1: Locate all files that belong to this app
    parts = find_apk_parts (args.base_path)
    logger.info (f"Found parts: {get_full_filelist (parts, True)}")

    main_apk_path = parts ["main"]
    mod_apk_path = OUT_DIR / main_apk_path.name

    # 2: Find the entry point(s)
    entry_points = get_entry_points (main_apk_path)

    if not entry_points:
        logger.error ("Couldn't locate the entry point")
        sys_exit (-2)

    logger.info (f"Found entry point(s): {entry_points}")

    # 3: Patch the entrypoints' Bytecode
    patched = patch_bytecode (main_apk_path, mod_apk_path, entry_points)
    if not patched:
        logger.critical ("Couldn't patch the Bytecode")
        sys_exit (-3)

    # 4: Download Frida and add it to the lib/ directory
    frida_script = None
    if args.frida_script:
        frida_script = args.frida_script.read ()
        logger.debug (f"Using the following Frida script:\n{frida_script.decode ('utf-8')}\n")

    gadget_config = None
    if args.gadget_config:
        gadget_config = args.gadget_config.read ()
        logger.debug (f"Using the following Gadget config:\n{gadget_config.decode ('utf-8')}\n")

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
    if args.fix_manifest:
        tmp_mod = mod_apk_path.with_suffix (".tmp")
        fix_manifest (mod_apk_path, tmp_mod)
        move (tmp_mod, mod_apk_path)

    # 6: copy everything (even the items we haven't modified) to OUT_DIR
    files = get_full_filelist (parts)

    for f in files:
        out_path = OUT_DIR / f.name
        logger.debug (f"Processing {out_path}")

        if not out_path.exists ():
            logger.debug (f"Copying unmodified file: {f}")
            copy (f, out_path)

    # 7: zipalign everything
        logger.debug ("Zipaligning...")
        Patcher.zipAlign (str (out_path))

    # 8: sign everything
        # We have to sign all parts with the same key, regardless of whether
        # we modified them or not
        logger.debug ("Signing...")
        tmp_file = str (Patcher.signApk (str (out_path), keystore_data))
        move (tmp_file, out_path)

    logger.success (f"[+] All done! The output APK can be found under {OUT_DIR}")
