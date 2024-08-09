# APK patcher

When trying to modify an android application, [Frida](frida.re) comes really handy.
However, on non-rooted devices it can sometimes be difficult to inject the gadget into the apk.

~~With single, fat, APKs, that's not much of an issue because there are already several tools that work really well, and it can also be done manually with `apktool`.~~
This is in my experience less and less true, since I encounter every time more APKs that, one way or another, break something along the process.
Since `apktool` decodes all resources, just a missing reference makes the whole process fail.

On the other hand, [split APKs](https://developer.android.com/guide/app-bundle) (those that come with not only a `base.apk`, but also other files like `*_config.xxhdpi.apk` et
al.) are harder to recompile, because there are certain dependencies between those different files, and fixing all the resource IDs (which has to be done before `apktool` lets
you merge all into a fat APK) is a pain that not always fully works.


This script aims to help with the injection task, by modifying the least amount of files possible so there are no issues later with the resources.

# Install pre-requisites

It's advised to create a virtualenv to install the dependencies:
```
$ virtualenv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements
```

Additionally, the following Java libraries must be present for the patcher to work end-to-end:
  - [./java_libs/apksig-8.7.0-alpha04.jar](https://dl.google.com/android/maven2/com/android/tools/build/apksig/8.7.0-alpha04/apksig-8.7.0-alpha04.jar)
  - [./java_libs/dexlib2-3.0.7-d09ec39b-dirty.jar](https://github.com/Foo-Manroot/smali)
  - [./java_libs/guava-33.2.1-jre.jar](https://repo1.maven.org/maven2/com/google/guava/guava/33.2.1-jre/guava-33.2.1-jre.jar)
  - [./java_libs/zipalign-java-v1.1.3.jar](https://jitpack.io/#Iyxan23/zipalign-java/v1.1.3)
  - ./Java/APK patcher/app/build/libs/app.jar

# Usage

Just run the script and read the help message:
```
$ python apk-patcher.py -h
usage: APK patcher [-h] [-f FIX_MANIFEST] [-c GADGET_CONFIG] [-v] [-l frida_script] base_path

Script to automate the decompilation, patch and rebuild of any Android split applications (those apps that have base.apk, plus .config.<something>.apk) to inject the provided Frida script.

positional arguments:
  base_path             Common prefix for all the split apk files.
                        For example, if we have:
                          - com.example.1234.apk
                          - com.example.1234.config.armeabi_v7a.apk
                          - com.example.1234.config.en.apk
                          - com.example.1234.config.xxhdpi.apk

                        'base-name' must be "com.example.1234." (note the dot at the end)

options:
  -h, --help            show this help message and exit
  -f FIX_MANIFEST, --fix_manifest FIX_MANIFEST
                        If set, the script will attempt to modify AndroidManifest.xml to set extractNativeLibs=true.
                        ATTENTION: it may cause problems like 'INSTALL_PARSE_FAILED_UNEXPECTED_EXCEPTION' on installation.
  -c GADGET_CONFIG, --config GADGET_CONFIG
                        Path to a custom Gadget config ( https://frida.re/docs/gadget/ )
  -v, --verbose         Increase the verbosity. Can be specified up to 3 times.
  -l frida_script, --load frida_script
                        The JS file to patch into the apk.
```

# Comparison with other tools

There are other tools which aim to do the same thing. For example:
  - [APK patcher](https://gitlab.com/MadSquirrels/mobile/apkpatcher) - not related to this project; I only discovered it while researching for libraries to [modify AXML](https://gitlab.com/MadSquirrels/mobile/pyaxml)
  - [Apktool](https://github.com/iBotPeaches/Apktool)
  - [objection](https://github.com/sensepost/objection)
  - ... and many, many others

However, as far as my research goes, all of them rely on OS commands to execute the same tools in the background:
  - [baksmali / smali](https://github.com/google/smali)
  - [zipalign](https://developer.android.com/tools/zipalign)
  - [apksigner](https://developer.android.com/tools/apksigner)


This poses two problems from my point of view:
  1. If one of those base tools fail (for example, `zipalign` on Kali has been giving me quite a lot of [errors](https://github.com/rapid7/metasploit-framework/issues/18301) like [undefined symbol](https://superuser.com/questions/1802392/how-to-fix-error-zipalign-symbol-lookup-error-zipalign-undefined-symbol-zn1)), _all_ tools will fail at the same step.
  2. Relying on executing OS commands poses the risk of something going wrong (for example, the output format changes slightly, and the parsing is off from there) without noticing, for example.

Therefore, I decided to implement all using those tools as libraries; or, when not possible, using alternative libraries which perform the same task.

# Future work

If you want to contribute, you can take a look into the following open topics:
  - [ ] Add more Frida scripts. For example:
    - [ ] Remove common ads and trackers
    - [ ] Disable cert pinning (besides the [common methods](https://codeshare.frida.re/@akabe1/frida-multiple-unpinning/)). A good idea is [to inject our own root CA](https://gitlab.com/MadSquirrels/mobile/apkpatcher/-/blob/8c7d96b8b6f132d628ea7564251f19f1c6172be0/src/apkpatcher/__init__.py#L70))
	- [ ] Disable root detection
  - [ ] Introduce proper logging
  - [ ] Dafuq is Revolut (com.revolut.revolut) to detect Frida even before it even loads ??


# Aknowledgments

This tool wouldn't have been possible without the invaluable research and effort of the third-party libraries I'm relying on, besides the regular ones (Java and Python standard libs, `requests`, ...):
  - [androguard](https://androguard.readthedocs.io/en/latest/index.html), to parse AXML (to decode the AndroidManifest.xml) and DEX files.
  - [pyaxml](https://gitlab.com/MadSquirrels/mobile/pyaxml), to patch AXML.
  - [JPype](https://jpype.readthedocs.io/en/latest/), to run the Java methods from within Python.
  - [baksmali / smali](https://github.com/google/smali), to inject the custom instructions into the appropriate DEX files.
  - [zipalign-java](https://github.com/Iyxan23/zipalign-java), to align the Zip files like the Android Runtime expects.
  - [apksig](https://maven.google.com/web/index.html#com.android.tools.build:apksig), to sign the final APKs.
  - And, of course, the other (probably) dozens of libraries that each of those tools rely on...
