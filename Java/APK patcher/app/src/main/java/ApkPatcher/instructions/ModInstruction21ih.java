package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction21ih;

public class ModInstruction21ih implements Instruction21ih {
    
    private final Instruction21ih originalInstr;
    
    public ModInstruction21ih (Instruction originalInstr) {

        Instruction21ih i = (Instruction21ih) originalInstr;

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
    public short getHatLiteral () {
        return originalInstr.getHatLiteral ();
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
