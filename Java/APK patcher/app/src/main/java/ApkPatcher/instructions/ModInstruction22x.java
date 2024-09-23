package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction22x;

public class ModInstruction22x implements Instruction22x {
    
    private final Instruction22x originalInstr;
    
    public ModInstruction22x (Instruction originalInstr) {

        Instruction22x i = (Instruction22x) originalInstr;

        this.originalInstr = i;
    }

    @Override
    public int getRegisterA() {
        
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
