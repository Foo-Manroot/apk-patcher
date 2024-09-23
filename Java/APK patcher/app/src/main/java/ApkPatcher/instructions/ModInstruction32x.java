package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction32x;

public class ModInstruction32x implements Instruction32x {
    
    private final Instruction32x originalInstr;
    
    public ModInstruction32x (Instruction originalInstr) {

        Instruction32x i = (Instruction32x) originalInstr;

        this.originalInstr = i;
    }

    @Override
    public int getRegisterA () {
        
        return originalInstr.getRegisterA () + 1;
    }
    
    @Override
    public int getRegisterB () {

        return originalInstr.getRegisterB () + 1;
    }

    /* ------------ */
    /* Boring stuff */
    /* ------------ */
    
    @Override
    public Opcode getOpcode () {
        return originalInstr.getOpcode ();
    }

    @Override
    public int getCodeUnits () {
        return originalInstr.getCodeUnits ();
    }
}
