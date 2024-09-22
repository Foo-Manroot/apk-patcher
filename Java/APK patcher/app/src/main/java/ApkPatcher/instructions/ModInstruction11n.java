package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction11n;

public class ModInstruction11n implements Instruction11n {
    
    private final Instruction11n originalInstr;
    
    public ModInstruction11n (Instruction originalInstr) {

        Instruction11n i = (Instruction11n) originalInstr;

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

    @Override
    public int getNarrowLiteral () {
        return originalInstr.getNarrowLiteral ();
    }

    @Override
    public long getWideLiteral () {
        return originalInstr.getWideLiteral ();
    }
}
