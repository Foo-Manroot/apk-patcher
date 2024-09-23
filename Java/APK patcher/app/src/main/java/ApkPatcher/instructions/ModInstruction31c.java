package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction31c;
import com.android.tools.smali.dexlib2.iface.reference.Reference;

public class ModInstruction31c implements Instruction31c {
    
    private final Instruction31c originalInstr;
    
    public ModInstruction31c (Instruction originalInstr) {

        Instruction31c i = (Instruction31c) originalInstr;

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
    public Reference getReference() {
        return originalInstr.getReference ();
    }

    @Override
    public int getReferenceType() {
        return originalInstr.getReferenceType ();
    }
}
