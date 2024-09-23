package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction31i;

public class ModInstruction31i implements Instruction31i {
    
    private final Instruction31i originalInstr;
    
    public ModInstruction31i (Instruction originalInstr) {

        Instruction31i i = (Instruction31i) originalInstr;

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
