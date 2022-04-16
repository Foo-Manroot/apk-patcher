# APK patcher

When trying to modify an android application, [Frida](frida.re) comes really handy.
However, on non-rooted devices it can sometimes be difficult to inject the gadget into the
apk.

With single, fat, APKs, that's not much of an issue because there are already several
tools that work really well, and it can also be done manually with `apktool`.

However, [split APKs](https://developer.android.com/guide/app-bundle) (those that come
with not only a `base.apk`, but also other files like `*_config.xxhdpi.apk` et al.) are
harder to recompile, because there are certain dependencies between those different files,
and fixing all the resource IDs (which has to be done before `apktool` lets you merge all
into a fat APK) is a pain that not always fully works.



This scripts aims to help with this task, by modifying the least amount of files possible
so there are no issues later with the resources.

# Usage

Just run the script and read the help message:
```
$ ./split-apk-patcher.sh -h
Foo-Manroot
Last change: 2022-04-16
v1.0

Script to automate the decompilation, patch and rebuild of any Android split applications
(those apps that have base.apk, plus .config.<something>.apk) to inject the provided
Frida script.

Usage:
./split-apk-patcher.sh <base-name> <frida-script>

Where:
	'base-name' is the common prefix for all the split apk files.
		For example, if we have:
			com.example.1234.apk
			com.example.1234.config.armeabi_v7a.apk
			com.example.1234.config.en.apk
			com.example.1234.config.xxhdpi.apk

		'base-name' MUST BE => "com.example.1234"

	'frida-script' is the JS file to add to the app's lib directory.
```

# Future work

If you want to contribute, you can take a look into the following open topics:
  - [] Add more scripts. For example:
    - [] Remove common ads and trackers
    - [] Disable cert pinning (besides the [common methods](https://codeshare.frida.re/@akabe1/frida-multiple-unpinning/))
	- [] Disable root detection
  - [] Add another script for non-split apks (although [objection](https://github.com/sensepost/objection) tends to do a good job with that)
  - [] Test more APKs. Currently tested to be working on:
    - [x] com.tinder.12020070
	- [x] ch.admin.swisstopo (version 1.6)
	- [] ch.coop.supercard
	- [] ch.migros.app
