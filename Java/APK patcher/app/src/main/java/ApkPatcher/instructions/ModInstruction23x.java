package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction23x;

public class ModInstruction23x implements Instruction23x {
    
    private final Instruction23x originalInstr;
    
    public ModInstruction23x (Instruction originalInstr) {

        Instruction23x i = (Instruction23x) originalInstr;

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
    
    @Override
    public int getRegisterC () {
        return originalInstr.getRegisterC () + 1;
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
