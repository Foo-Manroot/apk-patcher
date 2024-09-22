package ApkPatcher.instructions;

import com.android.tools.smali.dexlib2.Opcode;
import com.android.tools.smali.dexlib2.iface.instruction.Instruction;
import com.android.tools.smali.dexlib2.iface.instruction.formats.Instruction35c;
import com.android.tools.smali.dexlib2.iface.reference.Reference;

public class ModInstruction35c implements Instruction35c {
    
    private final Instruction35c originalInstr;
    private final int regCount;
    
    public ModInstruction35c (Instruction originalInstr) {

        Instruction35c i = (Instruction35c) originalInstr;

        this.originalInstr = i;
        this.regCount = i.getRegisterCount ();
    }

    @Override
    public int getRegisterC () {
        
        return regCount >= 1 ?
                originalInstr.getRegisterC () + 1
                : originalInstr.getRegisterC ();
    }

    @Override
    public int getRegisterD () {

        return regCount >= 2 ?
                originalInstr.getRegisterD () + 1
                : originalInstr.getRegisterD ();
    }

    @Override
    public int getRegisterE () {
        
        return regCount >= 3 ?
                originalInstr.getRegisterE () + 1
                : originalInstr.getRegisterE ();
    }

    @Override
    public int getRegisterF () {

        return regCount >= 4 ?
                originalInstr.getRegisterF () + 1
                : originalInstr.getRegisterF ();
    }

    @Override
    public int getRegisterG () {

        return regCount >= 5 ?
                originalInstr.getRegisterG () + 1
                : originalInstr.getRegisterG ();
    }

    @Override
    public int getRegisterCount () {

        return regCount;
    }
    
    /* ------------ */
    /* Boring stuff */
    /* ------------ */

    @Override
    public Opcode getOpcode() {
        
        return originalInstr.getOpcode ();
    }

    @Override
    public int getCodeUnits() {
        
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
