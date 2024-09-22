package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction21c;
import com.android.tools.smali.dexlib2.iface.reference.Reference;

public class ModInstruction21c implements Instruction21c {
    
    private final Instruction21c originalInstr;
    
    public ModInstruction21c (Instruction originalInstr) {

        Instruction21c i = (Instruction21c) originalInstr;

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
