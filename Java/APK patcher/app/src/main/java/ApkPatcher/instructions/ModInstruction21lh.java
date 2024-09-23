package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction21lh;

public class ModInstruction21lh implements Instruction21lh {
    
    private final Instruction21lh originalInstr;
    
    public ModInstruction21lh (Instruction originalInstr) {

        Instruction21lh i = (Instruction21lh) originalInstr;

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
    public long getWideLiteral () {
        return originalInstr.getWideLiteral ();
    }

    @Override
    public short getHatLiteral () {
        return originalInstr.getHatLiteral ();
    }
}
