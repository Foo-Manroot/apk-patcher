package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction22t;

public class ModInstruction22t implements Instruction22t {
    
    private final Instruction22t originalInstr;
    
    public ModInstruction22t (Instruction originalInstr) {

        Instruction22t i = (Instruction22t) originalInstr;

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

    @Override
    public int getCodeOffset () {
        return originalInstr.getCodeOffset ();
    }
}
