package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction22c;
import com.android.tools.smali.dexlib2.iface.reference.Reference;

public class ModInstruction22c implements Instruction22c {
    
    private final Instruction22c originalInstr;
    
    public ModInstruction22c (Instruction originalInstr) {

        Instruction22c i = (Instruction22c) originalInstr;

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
    public Reference getReference () {
        return originalInstr.getReference ();
    }

    @Override
    public int getReferenceType () {
        return originalInstr.getReferenceType ();
    }
}
