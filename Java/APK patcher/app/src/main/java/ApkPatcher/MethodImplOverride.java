package ApkPatcher;

import ApkPatcher.instructions.ModInstruction11n;
import ApkPatcher.instructions.ModInstruction11x;
import ApkPatcher.instructions.ModInstruction12x;
import ApkPatcher.instructions.ModInstruction21c;
import ApkPatcher.instructions.ModInstruction21ih;
import ApkPatcher.instructions.ModInstruction21lh;
import ApkPatcher.instructions.ModInstruction21s;
import ApkPatcher.instructions.ModInstruction21t;
import ApkPatcher.instructions.ModInstruction22b;
import ApkPatcher.instructions.ModInstruction22c;
import ApkPatcher.instructions.ModInstruction22cs;
import ApkPatcher.instructions.ModInstruction22s;
import ApkPatcher.instructions.ModInstruction22t;
import ApkPatcher.instructions.ModInstruction22x;
import ApkPatcher.instructions.ModInstruction23x;
import ApkPatcher.instructions.ModInstruction31c;
import ApkPatcher.instructions.ModInstruction31i;
import ApkPatcher.instructions.ModInstruction31t;
import ApkPatcher.instructions.ModInstruction32x;
import ApkPatcher.instructions.ModInstruction35c;
import ApkPatcher.instructions.ModInstruction35mi;
import ApkPatcher.instructions.ModInstruction35ms;
import ApkPatcher.instructions.ModInstruction45cc;
import ApkPatcher.instructions.ModInstruction51l;
import static com.android.tools.smali.dexlib2.Format.Format11n;
import static com.android.tools.smali.dexlib2.Format.Format12x;
import static com.android.tools.smali.dexlib2.Format.Format21ih;
import static com.android.tools.smali.dexlib2.Format.Format21lh;
import static com.android.tools.smali.dexlib2.Format.Format21s;
import static com.android.tools.smali.dexlib2.Format.Format21t;
import static com.android.tools.smali.dexlib2.Format.Format22b;
import static com.android.tools.smali.dexlib2.Format.Format22c;
import static com.android.tools.smali.dexlib2.Format.Format22cs;
import static com.android.tools.smali.dexlib2.Format.Format22s;
import static com.android.tools.smali.dexlib2.Format.Format22t;
import static com.android.tools.smali.dexlib2.Format.Format23x;
import static com.android.tools.smali.dexlib2.Format.Format31c;
import static com.android.tools.smali.dexlib2.Format.Format31i;
import static com.android.tools.smali.dexlib2.Format.Format31t;
import static com.android.tools.smali.dexlib2.Format.Format35c;
import static com.android.tools.smali.dexlib2.Format.Format35mi;
import static com.android.tools.smali.dexlib2.Format.Format35ms;
import static com.android.tools.smali.dexlib2.Format.Format45cc;
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

                case Format21lh:
                    modded.add (new ModInstruction21lh (instr));
                    break;

                case Format21s:
                    modded.add (new ModInstruction21s (instr));
                    break;

                case Format21t:
                    modded.add (new ModInstruction21t (instr));
                    break;

                case Format22b:
                    modded.add (new ModInstruction22b (instr));
                    break;

                case Format22c:
                    modded.add (new ModInstruction22c (instr));
                    break;

                case Format22cs:
                    modded.add (new ModInstruction22cs (instr));
                    break;

                case Format22s:
                    modded.add (new ModInstruction22s (instr));
                    break;

                case Format22t:
                    modded.add (new ModInstruction22t (instr));
                    break;

                case Format22x:
                    modded.add (new ModInstruction22x (instr));
                    break;

                case Format23x:
                    modded.add (new ModInstruction23x (instr));
                    break;

                case Format31c:
                    modded.add (new ModInstruction31c (instr));
                    break;

                case Format31i:
                    modded.add (new ModInstruction31i (instr));
                    break;

                case Format31t:
                    modded.add (new ModInstruction31t (instr));
                    break;

                case Format32x:
                    modded.add (new ModInstruction32x (instr));
                    break;

                case Format35c:
                    modded.add (new ModInstruction35c (instr));
                    break;

                case Format35mi:
                    modded.add (new ModInstruction35mi (instr));
                    break;

                case Format35ms:
                    modded.add (new ModInstruction35ms (instr));
                    break;

                case Format45cc:
                    modded.add (new ModInstruction45cc (instr));
                    break;

                case Format51l:
                    modded.add (new ModInstruction51l (instr));
                    break;
                    
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
