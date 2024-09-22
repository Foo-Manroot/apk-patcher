package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction11x;

public class ModInstruction11x implements Instruction11x {
    
    private final Instruction11x originalInstr;
    
    public ModInstruction11x (Instruction originalInstr) {

        Instruction11x i = (Instruction11x) originalInstr;

        this.originalInstr = i;
    }

    @Override
    public int getRegisterA() {
        
        return originalInstr.getRegisterA () + 1;
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
