package ApkPatcher;

import ApkPatcher.instructions.ModInstruction11n;
import ApkPatcher.instructions.ModInstruction11x;
import ApkPatcher.instructions.ModInstruction12x;
import ApkPatcher.instructions.ModInstruction21c;
import ApkPatcher.instructions.ModInstruction21ih;
import ApkPatcher.instructions.ModInstruction35c;
import static com.android.tools.smali.dexlib2.Format.Format11n;
import static com.android.tools.smali.dexlib2.Format.Format12x;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedMethodImplementation;
import com.android.tools.smali.dexlib2.iface.ExceptionHandler;
import com.android.tools.smali.dexlib2.iface.MethodImplementation;
import com.android.tools.smali.dexlib2.iface.TryBlock;
import com.android.tools.smali.dexlib2.iface.debug.DebugItem;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.util.MethodUtil;
import java.util.ArrayList;
import java.util.List;


/**
 * Modification of the MethodImplementaiton to increment the register count.
 * The `getModInstructions()` method also modifies the original instructions to
 * also increase the registers they use.
 */
public class MethodImplOverride implements MethodImplementation {
    
    private final MethodImplementation originalMethod;
    
    public MethodImplOverride (MethodImplementation originalMethod) {

        this.originalMethod = originalMethod;
    }
    
    /**
     * Returns the number of registers that are used as a parameter (as opposed
     * to a local register).
     */
    public int getParamCount () {
        
        int paramCount = 0;
        DexBackedMethodImplementation dexMethod;
        
        if (originalMethod instanceof DexBackedMethodImplementation) {
            
            dexMethod = (DexBackedMethodImplementation) originalMethod;

            paramCount = MethodUtil.getParameterRegisterCount (dexMethod.method);    
        }

        return paramCount;
    }
    
    /**
     * Returns "true" if no register is available for the gadget injection and,
     * therefore, an extra register needs to be used.
     */
    public boolean needsExtraRegister () {
        
        int originalCount = originalMethod.getRegisterCount ();
        int paramCount = getParamCount ();

        return originalCount == paramCount;
    }
    
    /**
     * Returns the original instructions, using one register more to account for
     * the extra register used by the injection stub.
     */
    public Iterable<? extends Instruction> getModInstructions () {

        ArrayList<Instruction> modded = new ArrayList<>();
        
        for (Instruction instr : originalMethod.getInstructions ()) {
            
            switch (instr.getOpcode ().format) {
                
                case Format35c:
                    modded.add (new ModInstruction35c (instr));
                    break;
                    
                case Format11n:
                    modded.add (new ModInstruction11n (instr));
                    break;
                    
                case Format11x:
                    modded.add (new ModInstruction11x (instr));
                    break;
                
                case Format12x:
                    modded.add (new ModInstruction12x (instr));
                    break;

                case Format21c:
                    modded.add (new ModInstruction21c (instr));
                    break;

                case Format21ih:
                    modded.add (new ModInstruction21ih (instr));
                    break;

                /**
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction21lh.java:public interface Instruction21lh extends OneRegisterInstruction, LongHatLiteralInstruction {

./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction21s.java:public interface Instruction21s extends OneRegisterInstruction, NarrowLiteralInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction21t.java:public interface Instruction21t extends OneRegisterInstruction, OffsetInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22b.java:public interface Instruction22b extends TwoRegisterInstruction, NarrowLiteralInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22c.java:public interface Instruction22c extends TwoRegisterInstruction, ReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22cs.java:public interface Instruction22cs extends TwoRegisterInstruction, FieldOffsetInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22s.java:public interface Instruction22s extends TwoRegisterInstruction, NarrowLiteralInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22t.java:public interface Instruction22t extends TwoRegisterInstruction, OffsetInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction22x.java:public interface Instruction22x extends TwoRegisterInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction23x.java:public interface Instruction23x extends ThreeRegisterInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction31c.java:public interface Instruction31c extends OneRegisterInstruction, ReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction31i.java:public interface Instruction31i extends OneRegisterInstruction, NarrowLiteralInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction31t.java:public interface Instruction31t extends OneRegisterInstruction, OffsetInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction32x.java:public interface Instruction32x extends TwoRegisterInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction35c.java:public interface Instruction35c extends FiveRegisterInstruction, ReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction35mi.java:public interface Instruction35mi extends FiveRegisterInstruction, InlineIndexInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction35ms.java:public interface Instruction35ms extends FiveRegisterInstruction, VtableIndexInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction3rc.java:public interface Instruction3rc extends RegisterRangeInstruction, ReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction3rmi.java:public interface Instruction3rmi extends RegisterRangeInstruction, InlineIndexInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction3rms.java:public interface Instruction3rms extends RegisterRangeInstruction, VtableIndexInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction45cc.java:public interface Instruction45cc extends FiveRegisterInstruction, DualReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction4rcc.java:public interface Instruction4rcc extends RegisterRangeInstruction, DualReferenceInstruction {
./src/main/java/com/android/tools/smali/dexlib2/iface/instruction/formats/Instruction51l.java:public interface Instruction51l extends OneRegisterInstruction,
                 */
                    
                default:
                    /* No registers used -> no mod needed */
                    modded.add (instr);
            }
        }
        
        return modded;
    }
    
    /* ---------------------------- */
    /* Implementation of interface: */
    /* ---------------------------- */

    @Override public int getRegisterCount () {

        int originalCount = originalMethod.getRegisterCount ();
        
        /* If all registers are parameters, a new one has to be added for the
        gadget injection. Otherwise, it's not needed */
        return needsExtraRegister () ? originalCount + 1 : originalCount;
    }

    @Override
    public Iterable<? extends Instruction> getInstructions () {
        
        return needsExtraRegister () ?
                getModInstructions ()
                : originalMethod.getInstructions ();
    }

    @Override
    public List<? extends TryBlock<? extends ExceptionHandler>> getTryBlocks () {
        return originalMethod.getTryBlocks ();
    }

    @Override
    public Iterable<? extends DebugItem> getDebugItems () {
        return originalMethod.getDebugItems ();
    }
}
