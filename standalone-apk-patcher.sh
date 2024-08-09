#!/bin/sh

AUTHORS="Foo-Manroot"
LAST_MODIF_DATE="2022-04-16"
VERSION="v1.0"

HELP_MSG="$AUTHORS
Last change: $LAST_MODIF_DATE
$VERSION

Script to automate the decompilation, patch and rebuild of any Android standalone
applications (which contain only 'base.apk', as opposed to split apks) to inject the
provided Frida script.

Usage:
$0 <apk-name> <frida-script>

Where:
	'apk-name' is the full path to the apk that will be patched.

	'frida-script' is the JS file to add to the app's lib directory.
"

############
## CONFIG ##
############

GADGET_CONFIG="
{
  \"interaction\": {
    \"type\": \"listen\",
    \"address\": \"127.0.0.1\",
    \"port\": 27042,
    \"on_port_conflict\": \"fail\",
    \"on_load\": \"wait\"
  }
}
"

# Location of the generated APKs
OUT_DIR="$(pwd)/patched/"

# One could say that it's easier to receive it as a parameter... XD
KEYSTORE_B64="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"

#####################################################
#####################################################
#####################################################

# Checks that all the needed tools are present
# Tested versions:
#		aapt2 -> v0.2-7929954
#		apksigner -> 0.9
#		smali/baksmali -> 2.5.2-2771eae0-dirty
#
# Tested apps:
#		ch.coop.supercard
errors=0
for req in \
		aapt2 \
		awk \
		zipalign \
		apksigner \
		curl \
		zip \
		unzip \
		unxz
do
	if ! command -v "$req" >/dev/null
	then
		printf "Requirement not found: '%s'\n" "$req"
		printf "Please, install it or add it to your \$PATH\n"

		errors=$((errors + 1))
	fi
done


if [ $errors -ne 0 ]
then
	exit $errors
fi


# ---------------------------------------------------------------------------------------

# Checks arguments (only 2 positional args allowed, and required)
if [ $# -ne 2 ]
then
	printf "%s\n" "$HELP_MSG"
	exit 1
fi

if [ "$1" = "-h" ] || [ "$1" = "--help" ] \
	|| [ "$2" = "-h" ] || [ "$2" = "--help" ]
then
	printf "%s\n" "$HELP_MSG"
	exit 0
fi

# Check the required files exist
APK_NAME="$(basename "$1")"
ORIGINAL_PATH="$(dirname "$1")"

if ! [ -r  "$ORIGINAL_PATH/$APK_NAME" ]
then
	printf "Error: any of these files is missing or read permission was not granted:\n"
	printf "\t%s.apk\n" "$ORIGINAL_PATH/$APK_NAME"
	exit 2
fi

# We need the full path for later
SCRIPT_FILE="$(readlink -f "$2")"

if ! [ -r "$SCRIPT_FILE" ]
then
	printf "Error: the JS file '%s' was not found or is not readable.\n" "$SCRIPT_FILE"
	exit 3
fi

# ---------------------------------------------------------------------------------------


cleanup() {
	printf "[%s] Cleaning up...\n" "$LOGNAME"
	rm -rf "$TEMP_DIR"
	printf "[%s] Done\n" "$LOGNAME"
}

# This is the actual start of the script itself

LOGNAME="$(basename "$0")"
#TEMP_DIR="$(mktemp -d)"
TEMP_DIR="$PWD/build" ; rm -rf "$TEMP_DIR" ; mkdir "$TEMP_DIR"
printf "[%s] Using '%s' as temp dir\n" "$LOGNAME" "$TEMP_DIR"


printf "\n[%s] ############## LOCATING MAIN ACTIVITY ################\n" "$LOGNAME"

# Idea to locate the main activity taken from
# https://github.com/sensepost/objection/blob/50817500c86509c1b32fa1b28faa53d6b3e4f835/objection/utils/patchers/android.py#L321
# It looks to be working for Objection, so I guess it should be also valid here...
main_act="$(aapt2 dump badging "$ORIGINAL_PATH/$APK_NAME" \
		| grep launchable-activity \
		| sed -e "s/launchable-activity: name='//" \
		| sed -e "s/'  label='.*//"
)"

if [ "$(echo "$main_act" | wc -w)" -ne 1 ]
then
	printf "\n[%s][ERROR] I didn't expect more (or less) than one main action :(\n" "$LOGNAME"
	# I guess the fix wouldn't be too complicated, but I prefer not to overthink it
	# if it's not necessary :D
	cleanup
	exit 2
fi

printf "[%s] Located class to patch: %s\n" "$LOGNAME" "$main_act"

# For the rest of the script we'll need to use the class path (a/b/C, instead of a.b.C)
main_class="$(printf "%s" "$main_act" | sed -e 's#\.#/#g')"

# Since we can't know which dex file contains the main activity, we have to extract
# everything and investigate a little bit...
TEMP_UNZIP="$TEMP_DIR/unzip"
found="X"
unzip -q "$ORIGINAL_PATH/$APK_NAME" -d "$TEMP_UNZIP"

printf "\n[%s] ############## SEARCHING MAIN CLASS ################\n" "$LOGNAME"

for candidate in $(find "$TEMP_UNZIP" -type f -name '*.dex' \
	-exec grep -le "$main_class" "{}" \;)
do
	# The constructor method should look like this (for example):
	# Lch/coop/supercard/SupercardActivity;-><init>()V
	#  (the constructor should always be void and accept no params)
	baksmali l m "$candidate" \
		| grep "L$main_class;-><init>()V" \
		&& found="$candidate" \
		&& break
done


if [ "X$found" = "XX" ]
then
	printf "\n[%s][ERROR] Couldn't find the correct class to patch...\n" "$LOGNAME"
	cleanup
	exit 2
fi

printf "\n[%s] ############## DISASSEMBLING %s ################\n" "$LOGNAME" "$found"

TEMP_SMALI="$TEMP_DIR/smali"
# I use the "--use-locals" flag because I have no clue how to deal with registers :D
# I don't use the "--classes "L$main_class;"" (which takes less to disassemble) because
# I need all of them to reassemble the whole file again
baksmali disassemble --use-locals "$found" -o "$TEMP_SMALI"

# Since the main class already contains the path, we can use it directly (baksmali
# extracts it into its full path, and appends the ".smali" extension)
FILE_TO_PATCH="$TEMP_SMALI/$main_class.smali"
mv -v "$FILE_TO_PATCH" "$FILE_TO_PATCH.ORIG"

awk '
	/.method( public)? constructor <init>\(\)V/ {
		found = 1
	}

	/.locals/ && found {
		print "    .locals", $2+1
		print "    const-string v2, \"gadget\""
		print "    invoke-static {v2}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V"

		found=0
		next
	}

	// { print }
' "$FILE_TO_PATCH.ORIG" > "$FILE_TO_PATCH"

printf "[%s] !!!!!! Make sure the injection was correctly done\n" "$LOGNAME"
printf "[%s] Here should appear the injected smali:\n" "$LOGNAME"
grep -C 1 'const-string v2, "gadget"' "$FILE_TO_PATCH"
printf "[%s] !!!! If nothing is showing on the above 3 lines, the patch failed :(" "$LOGNAME"

printf "\n[%s] ############## REASSEMBLING %s ################\n" "$LOGNAME" "$found"
smali assemble "$TEMP_SMALI" -o "$found"

printf "[%s] This is the configuration file to be added:\n" "$LOGNAME"
printf "%s" "$GADGET_CONFIG"

printf "\n[%s] ############## DOWNLOADING FRIDA ################\n" "$LOGNAME"

frida_archs="$(find "$TEMP_UNZIP/lib/" \
		-maxdepth 1 -mindepth 1 -type d \
		-exec basename "{}" \;
)"

for apk_arch in $frida_archs
do
	frida_arch=""
	#	- armeabi-v7a -> Frida "android-arm"
	#	- arm64-v8a   -> Frida "android-arm64"
	#	- x86         -> Frida "android-x86"
	#	- x86_64      -> Frida "android-x86_64"
	case "$apk_arch" in
		armeabi-v7a) frida_arch="android-arm" ;;
		arm64-v8a)   frida_arch="android-arm64" ;;
		x86)         frida_arch="android-x86" ;;
		x86_64)      frida_arch="android-x86_64" ;;
		*)
			printf "\n[%s][ERROR] Couldn't determine the required Frida architecture matching the string '%s' :(\n" "$LOGNAME" "$apk_arch"
			cleanup
			exit 2
	esac

	printf "[%s] Architecture(s) to use: %s\n" "$LOGNAME" "$frida_arch"
	# Taken from https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c?permalink_comment_id=3294173#gistcomment-3294173
	frida_base="https://github.com/frida/frida/releases"
	latest_frida="$(basename \
		"$(curl -fs -o/dev/null -w "%{redirect_url}" "$frida_base/latest")"
	)"

	gadget_url="$frida_base/download/$latest_frida/frida-gadget-$latest_frida-$frida_arch.so.xz"
	lib_dir="$TEMP_UNZIP/lib/$apk_arch"
	printf "[%s] Downloading %s\n" "$LOGNAME" "$gadget_url"
	curl -L "$gadget_url" -o "$lib_dir/libgadget.so.xz" -q#

	#7z x "$TEMP_DIR/libgadget.so.xz" -o"$TEMP_DIR" -bso0
	unxz "$lib_dir/libgadget.so.xz"

	printf "%s" "$GADGET_CONFIG" > "$lib_dir/libgadget.config.so"
	cp -v "$SCRIPT_FILE" "$lib_dir/libgadget.js.so"

done

PREVIOUS_PATH="$PWD"
cd "$TEMP_UNZIP" \
	|| (printf "[%s] Error during cd to %s\n" "$LOGNAME" "$TEMP_UNZIP" && exit)
rm -rf META-INF/*
# The libraries must not be compressed
# https://stackoverflow.com/a/55186445
# https://issuetracker.google.com/issues/37045367
zip -qn "resources.arsc:.so" -r "$TEMP_DIR/$APK_NAME.PATCHED.apk" ./*
cd "$PREVIOUS_PATH" \
	|| (printf "[%s] Error during cd to %s\n" "$LOGNAME" "$PREVIOUS_PATH" && exit)
rm -rf "$TEMP_UNZIP"





printf "\n[%s] ############## BUILDING FINAL APK ################\n" "$LOGNAME"
# Finally: rebuild, align and sign our new apk
printf "%s\n" "$KEYSTORE_B64" | base64 -d > "$TEMP_DIR/store.jks"

TEMP_BUILD="$TEMP_DIR/build/"
mkdir -p "$TEMP_BUILD"
cp "$TEMP_DIR/$APK_NAME.PATCHED.apk" "$TEMP_BUILD"



mkdir -p "$OUT_DIR"
for part in "$TEMP_BUILD/"*.apk
do
	zipalign -fp 4 "$part" "${part}_aligned"

	# Apparently, sometimes  "--min-sdk-version" is required (??)
	apksigner sign --ks "$TEMP_DIR/store.jks" --ks-pass pass:123456 \
		"${part}_aligned"

	mv "${part}_aligned" "$OUT_DIR/$(basename "$part")"

done

cleanup

printf "\n[%s] ############## ALL DONE ##############\n" "$LOGNAME"
printf "[%s] You can find here your APK ready to be installed (use \`adb install\`): %s\n" "$LOGNAME" "$OUT_DIR"
