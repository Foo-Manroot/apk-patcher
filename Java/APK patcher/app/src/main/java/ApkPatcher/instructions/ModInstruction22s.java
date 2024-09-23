package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction22s;

public class ModInstruction22s implements Instruction22s {
    
    private final Instruction22s originalInstr;
    
    public ModInstruction22s (Instruction originalInstr) {

        Instruction22s i = (Instruction22s) originalInstr;

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
    public int getNarrowLiteral () {
        return originalInstr.getNarrowLiteral ();
    }

    @Override
    public long getWideLiteral () {
        return originalInstr.getWideLiteral ();
    }
}
