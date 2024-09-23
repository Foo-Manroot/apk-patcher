package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction21s;

public class ModInstruction21s implements Instruction21s {
    
    private final Instruction21s originalInstr;
    
    public ModInstruction21s (Instruction originalInstr) {

        Instruction21s i = (Instruction21s) originalInstr;

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
