package ApkPatcher;

import com.android.apksig.ApkSigner;
import com.android.apksig.KeyConfig;
import com.android.apksig.apk.ApkFormatException;
import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.builder.MutableMethodImplementation;
import com.android.tools.smali.dexlib2.builder.instruction.BuilderInstruction21c;
import com.android.tools.smali.dexlib2.builder.instruction.BuilderInstruction35c;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedMethod;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedMethodImplementation;
import com.android.tools.smali.dexlib2.dexbacked.instruction.DexBackedInstruction;
import com.android.tools.smali.dexlib2.dexbacked.instruction.DexBackedInstruction10x;
import com.android.tools.smali.dexlib2.dexbacked.instruction.DexBackedInstruction35c;
import com.android.tools.smali.dexlib2.iface.DexFile;
import com.android.tools.smali.dexlib2.iface.MethodImplementation;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.immutable.reference.ImmutableMethodReference;
import com.android.tools.smali.dexlib2.immutable.reference.ImmutableStringReference;
import com.android.tools.smali.dexlib2.rewriter.DexRewriter;
import com.android.tools.smali.dexlib2.rewriter.Rewriter;
import com.android.tools.smali.dexlib2.rewriter.RewriterModule;
import com.android.tools.smali.dexlib2.rewriter.Rewriters;
import com.android.tools.smali.dexlib2.writer.io.MemoryDataStore;
import com.android.tools.smali.dexlib2.writer.pool.DexPool;
import com.iyxan23.zipalignjava.InvalidZipException;
import com.iyxan23.zipalignjava.ZipAlign;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.security.GeneralSecurityException;
import java.security.KeyFactory;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.security.interfaces.ECPrivateKey;
import java.security.spec.ECPublicKeySpec;
import java.security.spec.InvalidKeySpecException;
import java.util.ArrayList;
import java.util.List;


public class Patcher {

    /**
     * Adds the following instructions at the beginning of the specified method implementation:
     * <pre>
     * const-string v0, "gadget"
     * invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
     * </pre>
     *
     * @param implementation Method implementation to be patched.
     *
     * @return A copy of the original method implementation, with the prepended instructions.
     */
    private static MethodImplementation addPreamble (MethodImplementation implementation) {

        if (implementation == null) {
            return implementation;
        }
        
//        MutableMethodImplementation mutableImplementation = new MutableMethodImplementation (implementation);

        /* ~~We can use v0 because this is the first instruction (so, no other value was introduced
        yet) and we don't really care if the next instruction stomps it, after we've loaded our
        library~~ <-- Not true, unfortunately
	Turns out we do actually need to take care of this shit, because sometimes there are no local registers available.
	For example, with Flutter, only p0 is available:

		.method public constructor <init>()V
		    .registers 1

		    invoke-direct {p0}, Lio/flutter/embedding/android/f;-><init>()V

		    return-void
		.end method

	Since p0 is a parameter, we get `java.lang.VerifyError: Rejecting class [...] because it failed compile-time verification`

        MethodImplOverride takes care of returning an extra register when required.
       	*/
        MethodImplOverride implOverride = new MethodImplOverride (implementation);
        MutableMethodImplementation mutableImplementation = new MutableMethodImplementation (implOverride);
        
        // const-string v0, "gadget"
        mutableImplementation.addInstruction (0,
            new BuilderInstruction21c (
                Opcode.CONST_STRING, // Opcode opcode
                0, // int registerA
                new ImmutableStringReference("gadget") // Reference reference
            )
        );

        // invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
        List<String> args = new ArrayList<>();
        args.add("Ljava/lang/String;");

        mutableImplementation.addInstruction (1,
            new BuilderInstruction35c (
                Opcode.INVOKE_STATIC, // Opcode opcode
                1, // int registerCount
                0, // int registerC
                0, 0, 0, 0, // int registerD, int registerE, int registerF, int registerG,
                new ImmutableMethodReference ( // Reference reference
                    "Ljava/lang/System;",
                    "loadLibrary",
                    args,
                    "V"
                )
            )
        );

        return mutableImplementation;
    }

    /**
     * Patches the given method of the specified class within the provided dex file, and returns the
     * rewritten copy.
     *
     * @param input DexFile to patch.
     *
     * @param classToPatch Class name (e.g.: "Lcom/example/SomeClass;") to target.
     *
     * @param methodToPatch Method within the aforementioned class. This will be the target of the rewrite.
     *
     * @return The rewritten DexFile.
     */
    private static DexFile patchDex (DexBackedDexFile input, String classToPatch, String methodToPatch) {

        DexRewriter rewriter = new DexRewriter (new RewriterModule() {
            @Override
            public Rewriter<MethodImplementation> getMethodImplementationRewriter (Rewriters rewriters) {
                return (MethodImplementation impl) -> {
                    /* The input is a DexBackedDexFile, so this should be a safe assumption to make */
                    if (impl instanceof DexBackedMethodImplementation) {
                        DexBackedMethodImplementation methodImpl = (DexBackedMethodImplementation) impl;
                        DexBackedMethod method = methodImpl.method;

                        if (method.getDefiningClass ().equals (classToPatch)
                            && method.getName ().equals (methodToPatch)
                        ) {
                            return addPreamble (methodImpl);
                        }
                    }
                    return impl;
                };
            }
        });

        return rewriter.getDexFileRewriter ().rewrite (input);
    }

//    /**
//     * Extracts the specified entry from the InputStream, which is assumed to be a zip file.
//     * 
//     * @param inputStream Input stream, which is assumed to be a zip file. Can be opened like this (for example):
//     *          <pre>new FileInputStream (new File ("some_file.apk"))</pre>
//     */
//    private static ByteArrayOutputStream extractFileFromZip (InputStream inputStream, String pathToExtract) throws IOException {
//
//        ByteArrayOutputStream output = new ByteArrayOutputStream ();
//
//        try (ZipInputStream apkInput = new ZipInputStream (inputStream) ) {
//            
//            ZipEntry entry;
//            while ((entry = apkInput.getNextEntry ()) != null) {
//
//                /* Only full matches are accepted */
//                if (entry.getName ().equals (pathToExtract)) {
//                    System.out.println ("[+] Found entry " + pathToExtract + " within the APK file");
//
//                    byte[] tmpBuffer = new byte[4096];
//                    int length = 0;
//
//                    while ( (length = apkInput.read(tmpBuffer)) != -1 ) {
//                        output.write (tmpBuffer, 0, length);
//                    }
//                }
//            }
//        }
//
//        return output;
//    }
    
    /**
     * Locates the specified class and method within the given Dex file and patches it using {@link #addPreamble(com.android.tools.smali.dexlib2.iface.MethodImplementation) }
     * 
     * @param dexBytes Input stream with the raw bytes of the dex file
     * 
     * @param className Class name (e.g.: "Lcom/example/SomeClass;") to target.
     *
     * @param methodName Method within the aforementioned class. This will be the target of the rewrite.
     *
     * @return The rewritten DexFile, as a Byte stream.
     * 
     * @throws IOException If the input input stream could not be read properly.
     */
    public static ByteArrayOutputStream patchDexFile (ByteArrayInputStream dexBytes, String className, String methodName, int dexVersion) throws IOException {

//        methodName = "decryptWithBiometrics"; // TODO : remove
        if (dexBytes == null) {
            throw new IOException ("The provided DEX input stream is null.");
        }
        
        ByteArrayOutputStream output = new ByteArrayOutputStream ();
 
        Opcodes opcodes = dexVersion <= 0 ? Opcodes.getDefault () : Opcodes.forDexVersion (dexVersion);

        System.out.println ("[INFO][JAVA] Parsing DEX file " + className + "->" + methodName);
        DexBackedDexFile dex = DexBackedDexFile.fromInputStream (opcodes, dexBytes);
        System.out.println ("[DEBUG][JAVA] Size of the original DEX: " + dex.getFileSize () + " Bytes");
        
        DexFile rewritten = patchDex (dex, className, methodName);
        
        MemoryDataStore store = new MemoryDataStore ();
        DexPool.writeTo (store, rewritten);

        System.out.println ("[DEBUG][JAVA] Size of the new generated DEX: " + store.getSize () + " Bytes");

        output.write (store.getData ());

        return output;
    }
    
    /**
     * Overload of {@link #patchDexFile(java.io.ByteArrayInputStream, java.lang.String, java.lang.String, int) } using the default DEX version.
     */
    public ByteArrayOutputStream patchDexFile (ByteArrayInputStream dexBytes, String className, String methodName) throws IOException {

        return patchDexFile (dexBytes, className, methodName, -1);
    }

    // This seems to break shit
//    /**
//     * Writes the specified file (given as a full path) on the existing Zip file located at pathToZip with the given data.
//     * 
//     * @param pathToZip Path the Zip file to be modified.
//     * 
//     * @param file Full path of the target element within the Zip file. If it exists, it will be replaced.
//     * 
//     * @param data Data to be written inside the Zip file. The data is stored, not compressed
//     * 
//     * @throws IOException If there was any error handling the Zip file.
//     */
//    public static void writeToZip (String pathToZip, String file, byte[] data) throws IOException {
//
//        Path zipPath = Paths.get (pathToZip);
//
//        /* https://stackoverflow.com/a/58817834 */
//        Map<String, String> env = new HashMap<>();
//        // Store, do not compress
//        env.put ("noCompression", "true");
//        env.put ("compressionMethod ", "STORED");
//
//        try (FileSystem zipFs = FileSystems.newFileSystem (zipPath, env)) {
//            Path filePath = zipFs.getPath (file);
//
//            /* Parent files are not automatically created.
//            If the file is at the root, getParent () returns null */
//            if (filePath.getParent () != null) {
//
//                Files.createDirectories (filePath.getParent ());
//            }
//            
//            Files.write (filePath, data, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.CREATE);
//        }
//        System.out.println ("[INFO][JAVA] Data written to " + pathToZip + "!" + file);
//    }
    
    /**
     * Modifies the given zip file to align its contents to a 4-Byte boundary
     * 
     * @param zipPath Path to the Zip file to be aligned. This file will be overwritten.
     * 
     * @throws IOException If the given file does not exist or couldn't be read
     *
     * @throws com.iyxan23.zipalignjava.InvalidZipException If the given file is not a valid Zip file
     */
    public static void zipAlign (String zipPath) throws IOException, InvalidZipException {
        
        RandomAccessFile zipIn = new RandomAccessFile (zipPath, "r");
        ByteArrayOutputStream aligned_zip = new ByteArrayOutputStream ();

        ZipAlign.alignZip (zipIn, aligned_zip, 4, true);

        System.out.println ("[DEBUG][JAVA] Original Zip file: " + zipIn.length () + " Bytes // Aligned Zip file: " + aligned_zip.size () + " Bytes.");
        
        /* Overwrites the original file */        
        FileOutputStream zipOut = new FileOutputStream (zipPath);
        aligned_zip.writeTo (zipOut);
    }

    
    /**
     * Generates a new private key.
     * As far as I know, Android doesn't impose any restrictions on the keys that can be used, so I just used the simplest process to create an EC key, leaving
     * all default options.
     * Goes without saying, that this key should not be used for anything serious beyond the scope of apk-patcher.
     */
    public static PrivateKey genPrivKey () {

        PrivateKey priv = null;

        try {
            /* EC key sizes are smaller, so it can be embedded on the main script or whatever */
            KeyPairGenerator gen = KeyPairGenerator.getInstance ("EC");

            priv = gen.genKeyPair ().getPrivate ();

        } catch (NoSuchAlgorithmException ex) {
            /* Is there any system where no Elliptic Curve is implemented ?? */
            System.err.println ("[ERROR][JAVA] Couldn't generate a private key: " + ex.getMessage ());
        }

        return priv;
    }
    
    
    /**
     * Generates a self-signed certificate corresponding to the provided private key.
     * 
     * @param privKey The private key from where to generate the X.509 certificate. It is assumed to be an Elliptic-Curve key.
     */
    public static X509Certificate genCert (PrivateKey privKey) {
        
        X509Certificate cert = null;

        try {
            KeyFactory factory = KeyFactory.getInstance ("EC");
            
            ECPrivateKey privEC = (ECPrivateKey) privKey;
            
            ECPublicKeySpec pubSpec = new ECPublicKeySpec (
                    privEC.getParams ().getGenerator (),
                    privEC.getParams ()
                );

            PublicKey pub = factory.generatePublic (pubSpec);
            
        } catch (NoSuchAlgorithmException | InvalidKeySpecException ex) {

            System.err.println ("[ERROR][JAVA] Couldn't generate an X.509 certificate from the provided private key: " + ex.getMessage ());
        }
        
        return cert;
    }
    
    /**
     * Generates a SignerConfig object using the provided private key and certificate chain.
     * 
     * @param privKey Private key used to generate the signer config. Can be generated using {@link #genPrivKey() }
     * 
     * @param certificates Certificate chain to sign.
     */
    public static List<ApkSigner.SignerConfig> genSignerConfigs (PrivateKey privKey, List<X509Certificate> certificates) {
        
        List<ApkSigner.SignerConfig> configList = new ArrayList<>();

        KeyConfig keyConfig = new KeyConfig.Jca (privKey);

        ApkSigner.SignerConfig config = new ApkSigner.SignerConfig.Builder (
                "Foo-Manroot/apk-patcher",
                keyConfig,
                certificates
            ).build ();
        
        configList.add (config);
        
        return configList;
    }
    
    /**
     * Signs the specified APK according to the provided keys.
     * The following <b>assumptions</b> are made:
     * <ul>
     *      <li>The <b>password</b> of the KeyStore and the private key is always "<b>123456</b>"</li>
     *      <li>The <b>alias</b> of the key is "<b>alias</b>"</li>
     * </ul>
     * 
     * @param filename Path to the APK to sign.
     * 
     * @param keyStoreBytes Raw Bytes of the KeyStore to sign the APK. It is assumed to be a PKCS12 key-store.
     * 
     * 
     * @return The path to the signed APK. Copying the file directly from this method creates a lot of "FileSystemException: The process cannot access the file
     * because it is being used by another process" (at least on my end), so I just let it to the caller to overwrite the original APK (if desired).
     * 
     * @throws java.io.IOException If the KeyStore couldn't be read.
     * @throws GeneralSecurityException If the KeyStore couldn't be read or the signature process failed.
     */
    public static String signApk (String filename, byte[] keyStoreBytes) throws IOException, GeneralSecurityException {

        File apkFile = new File (filename);
        File tmpFile = new File (filename + "_signed.tmp");

        KeyStore store = KeyStore.getInstance ("pkcs12");
        store.load (
                new ByteArrayInputStream (keyStoreBytes),
                "123456".toCharArray ()
            );

        List<X509Certificate> certs = new ArrayList<>();

        /* If the hardcoded KeyStore is used, this should be a PrivateKey (actually, an RSAPrivateKey, but that doesn't matter)  */
        PrivateKey privKey = (PrivateKey) store.getKey ("alias", "123456".toCharArray ());
        Certificate cert = store.getCertificate ("alias");

        certs.add ((X509Certificate) cert);

        List<ApkSigner.SignerConfig> signerConfigs = genSignerConfigs (privKey, certs);
      
        ApkSigner signer = new ApkSigner.Builder (signerConfigs)
                .setDebuggableApkPermitted (true)
                .setInputApk (apkFile)
                .setOutputApk (tmpFile)
                .setV1SigningEnabled (true)
                .setV2SigningEnabled (true)
                .setV3SigningEnabled (true)
//                .setV4SigningEnabled (true)
//                .setV4ErrorReportingEnabled​ (true)
//                .setV4SignatureOutputFile (new File (outputFilename + ".idsig"))
//                .setOtherSignersSignaturesPreserved (true) // Not compatible with v3 Signing
                .setCreatedBy ("Foo-Manroot/apk-patcher")
                .build ();

        try {
            signer.sign ();

            System.out.println ("[DEBUG][JAVA] Apk signed.");

        } catch (IllegalStateException | ApkFormatException ex) {

            System.err.println ("[ERROR][JAVA] Error signing " + filename + ": " + ex.getMessage ());
        }

        return tmpFile.getAbsolutePath ();
    }

}
