#include "Feature.h"
using namespace llvm;

#define DEBUG_TYPE "feature"
#define PRINT outputFile

STATISTIC(NumGlobalVars, "Number of Global Variables referred to (number present)");
STATISTIC(GlobalVarUsage, "Number of Global Variable References (usages)");
STATISTIC(TotalInsts, "Number of instructions (of all types)");
STATISTIC(TotalBlocks, "Number of basic blocks");
STATISTIC(BlockLow, "Number of BB's with less than 15 instructions");
STATISTIC(BlockMid, "Number of BB's with instructions between [15, 500]");
STATISTIC(BlockHigh, "Number of BB's with more than 500 instructions");
STATISTIC(TotalFuncs, "Number of non-external functions");
STATISTIC(TotalMemInst, "Number of memory instructions");
STATISTIC(BeginPhi, "# of Phi-nodes at beginning of BB");
STATISTIC(ArgsPhi, "Total arguments to Phi nodes");
STATISTIC(BBNoPhi, "# of BB's with no Phi nodes");
STATISTIC(BB03Phi, "# of BB's with Phi node # in range (0, 3]");
STATISTIC(BBHiPhi, "# of BB's with more than 3 Phi nodes");
STATISTIC(BBNumArgsHi, "# of BB where total args for phi nodes > 5");
STATISTIC(BBNumArgsLo, "# of BB where total args for phi nodes is [1, 5]");
STATISTIC(testUnary, "Unary");
STATISTIC(binaryConstArg, "Binary operations with a constant operand");
STATISTIC(callLargeNumArgs, "# of calls with number of arguments > 4");
STATISTIC(returnInt, "# of calls that return an int");
STATISTIC(oneSuccessor, "# of BB's with 1 successor");
STATISTIC(twoSuccessor, "# of BB's with 2 successors");
STATISTIC(moreSuccessors, "# of BB's with >2 successors");
STATISTIC(onePred, "# of BB's with 1 predecessor");
STATISTIC(twoPred, "# of BB's with 2 predecessors");
STATISTIC(morePreds, "# of BB's with >2 predecessors");
STATISTIC(onePredOneSuc, "# of BB's with 1 predecessor and 1 successor");
STATISTIC(onePredTwoSuc, "# of BB's with 1 predecessor and 2 successors");
STATISTIC(twoPredOneSuc, "# of BB's with 2 predecessors and 1 successor");
STATISTIC(twoEach, "# of BB's with 2 predecessors and successors");
STATISTIC(moreEach, "# of BB's with >2 predecessors and successors");
STATISTIC(NumEdges, "# of edges");
STATISTIC(CriticalCount, "# of critical edges");
STATISTIC(BranchCount, "# of branches");
STATISTIC(numConstOnes, "# of occurrences of constant 1");
STATISTIC(numConstZeroes, "# of occurrences of constant 0");
STATISTIC(const32Bit, "# of occurrences of 32-bit integer constants");
STATISTIC(const64Bit, "# of occurrences of 64-bit integer constants");
STATISTIC(UncondBranches, "# of unconditional branches");
STATISTIC(NumGetElementPtrInst, "# of GetElementPtr insts");
STATISTIC(NumLoadInst, "# of Load insts");
STATISTIC(NumCallInst, "# of Call insts");
STATISTIC(NumInvokeInst, "# of Invoke insts");
STATISTIC(NumAllocaInst, "# of Alloca insts");
STATISTIC(NumStoreInst, "# of Store insts");
STATISTIC(NumAShrInst, "# of AShr insts");
STATISTIC(NumAddInst, "# of Add insts");
STATISTIC(NumSubInst, "# of Sub insts");
STATISTIC(NumAndInst, "# of And insts");
STATISTIC(NumOrInst, "# of Or insts");
STATISTIC(NumXorInst, "# of Xor insts");
STATISTIC(NumBitCastInst, "# of BitCast insts");
STATISTIC(NumICmpInst, "# of ICmp insts");
STATISTIC(NumLShrInst, "# of LShr insts");
STATISTIC(NumMulInst, "# of Mul insts");
STATISTIC(NumSExtInst, "# of SExt insts");
STATISTIC(NumZExtInst, "# of ZExt insts");
STATISTIC(NumSelectInst, "# of Select insts");
STATISTIC(NumShlInst, "# of Shl insts");

void printStats()
{
    std::ofstream outputFile;
    outputFile.open("./TMP_FEATURE.txt");
    PRINT << "NumGlobalVars " << NumGlobalVars << "\n";
    PRINT << "GlobalVarUsage " << GlobalVarUsage << "\n";
    PRINT << "TotalInsts " << TotalInsts << "\n";
    PRINT << "TotalBlocks " << TotalBlocks << "\n";
    PRINT << "BlockLow " << BlockLow << "\n";
    PRINT << "BlockMid " << BlockMid << "\n";
    PRINT << "BlockHigh " << BlockHigh << "\n";
    PRINT << "TotalFuncs " << TotalFuncs << "\n";
    PRINT << "TotalMemInst " << TotalMemInst << "\n";
    PRINT << "BeginPhi " << BeginPhi << "\n";
    PRINT << "ArgsPhi " << ArgsPhi << "\n";
    PRINT << "BBNoPhi " << BBNoPhi << "\n";
    PRINT << "BB03Phi " << BB03Phi << "\n";
    PRINT << "BBHiPhi " << BBHiPhi << "\n";
    PRINT << "BBNumArgsHi " << BBNumArgsHi << "\n";
    PRINT << "BBNumArgsLo " << BBNumArgsLo << "\n";
    PRINT << "testUnary " << testUnary << "\n";
    PRINT << "binaryConstArg " << binaryConstArg << "\n";
    PRINT << "callLargeNumArgs " << callLargeNumArgs << "\n";
    PRINT << "returnInt " << returnInt << "\n";
    PRINT << "oneSuccessor " << oneSuccessor << "\n";
    PRINT << "twoSuccessor " << twoSuccessor << "\n";
    PRINT << "moreSuccessors " << moreSuccessors << "\n";
    PRINT << "onePred " << onePred << "\n";
    PRINT << "twoPred " << twoPred << "\n";
    PRINT << "morePreds " << morePreds << "\n";
    PRINT << "onePredOneSuc " << onePredOneSuc << "\n";
    PRINT << "onePredTwoSuc " << onePredTwoSuc << "\n";
    PRINT << "twoPredOneSuc " << twoPredOneSuc << "\n";
    PRINT << "twoEach " << twoEach << "\n";
    PRINT << "moreEach " << moreEach << "\n";
    PRINT << "NumEdges " << NumEdges << "\n";
    PRINT << "CriticalCount " << CriticalCount << "\n";
    PRINT << "BranchCount " << BranchCount << "\n";
    PRINT << "numConstOnes " << numConstOnes << "\n";
    PRINT << "numConstZeroes " << numConstZeroes << "\n";
    PRINT << "const32Bit " << const32Bit << "\n";
    PRINT << "const64Bit " << const64Bit << "\n";
    PRINT << "UncondBranches " << UncondBranches << "\n";
    PRINT << "NumLoadInst " << NumLoadInst << "\n";
    PRINT << "NumCallInst " << NumCallInst << "\n";
    PRINT << "NumInvokeInst " << NumInvokeInst << "\n";
    PRINT << "NumAllocaInst " << NumAllocaInst << "\n";
    PRINT << "NumStoreInst " << NumStoreInst << "\n";
    PRINT << "NumGetElementPtrInst " << NumGetElementPtrInst << "\n";
    PRINT << "NumAShrInst " << NumAShrInst << "\n";
    PRINT << "NumLShrInst " << NumLShrInst << "\n";
    PRINT << "NumShlInst " << NumShlInst << "\n";
    PRINT << "NumAddInst " << NumAddInst << "\n";
    PRINT << "NumSubInst " << NumSubInst << "\n";
    PRINT << "NumMulInst " << NumMulInst << "\n";
    PRINT << "NumAndInst " << NumAndInst << "\n";
    PRINT << "NumOrInst " << NumOrInst << "\n";
    PRINT << "NumXorInst " << NumXorInst << "\n";
    PRINT << "NumBitCastInst " << NumBitCastInst << "\n";
    PRINT << "NumICmpInst " << NumICmpInst << "\n";
    PRINT << "NumSExtInst " << NumSExtInst << "\n";
    PRINT << "NumZExtInst " << NumZExtInst << "\n";
    PRINT << "NumSelectInst " << NumSelectInst << "\n";
    outputFile.close();
}

bool Feature::runOnModule(Module &M)
{
    for (auto &Global : M.getGlobalList())
    {
        NumGlobalVars++;
        if (auto *v = dyn_cast<Value>(&Global))
        {
            GlobalVarUsage += v->getNumUses();
        }
    }
    for (Function &F : M)
    {
        ++TotalFuncs;
        for (BasicBlock &BB : F)
        {
            ++TotalBlocks;
            Instruction *term = BB.getTerminator();
            unsigned numSuccessors = term->getNumSuccessors();
            if (numSuccessors == 1)
            {
                oneSuccessor++;
            }
            else if (numSuccessors == 2)
            {
                twoSuccessor++;
            }
            else if (numSuccessors > 2)
            {
                moreSuccessors++;
            }
            for (int i = 0; i < numSuccessors; i++)
            {
                NumEdges++;
                if (isCriticalEdge(term, i))
                {
                    CriticalCount++;
                }
            }
            unsigned numPreds = 0;
            for (pred_iterator pi = pred_begin(&BB), E = pred_end(&BB); pi != E; ++pi)
            {
                numPreds++;
            }
            if (numPreds == 1)
            {
                onePred++;
            }
            else if (numPreds == 2)
            {
                twoPred++;
            }
            else if (numPreds > 2)
            {
                morePreds++;
            }
            if (numPreds == 1 && numSuccessors == 1)
            {
                onePredOneSuc++;
            }
            else if (numPreds == 2 && numSuccessors == 1)
            {
                twoPredOneSuc++;
            }
            else if (numPreds == 1 && numSuccessors == 2)
            {
                onePredTwoSuc++;
            }
            else if (numPreds == 2 && numSuccessors == 2)
            {
                twoEach++;
            }
            else if (numPreds > 2 && numSuccessors > 2)
            {
                moreEach++;
            }

            unsigned tempCount = 0;
            bool isFirst = true;
            unsigned phiCount = 0;
            unsigned BBArgs = 0;
            for (Instruction &I : BB)
            {
                ++TotalInsts;
                if (auto *bi = dyn_cast<BranchInst>(&I))
                {
                    BranchCount++;
                    if (bi->isUnconditional())
                    {
                        UncondBranches++;
                    }
                }
                for (int i = 0; i < I.getNumOperands(); i++)
                {
                    Value *v = I.getOperand(i);
                    if (auto *c = dyn_cast<Constant>(v))
                    {
                        if (auto *ci = dyn_cast<ConstantInt>(c))
                        {
                            APInt val = ci->getValue();
                            unsigned bitWidth = val.getBitWidth();
                            if (bitWidth == 32)
                            {
                                const32Bit++;
                            }
                            else if (bitWidth == 64)
                            {
                                const64Bit++;
                            }
                            if (val == 1)
                            {
                                numConstOnes++;
                            }
                            else if (val == 0)
                            {
                                numConstZeroes++;
                            }
                        }
                    }
                }
                if (isa<BinaryOperator>(I))
                {
                    if (I.getOpcode() == Instruction::Add)
                    {
                        ++NumAddInst;
                    }
                    if (I.getOpcode() == Instruction::Sub)
                    {
                        ++NumSubInst;
                    }
                    if (I.getOpcode() == Instruction::Mul)
                    {
                        ++NumMulInst;
                    }
                    if (I.getOpcode() == Instruction::And)
                    {
                        ++NumAndInst;
                    }
                    if (I.getOpcode() == Instruction::Or)
                    {
                        ++NumOrInst;
                    }
                    if (I.getOpcode() == Instruction::Xor)
                    {
                        ++NumXorInst;
                    }
                    if (I.getOpcode() == Instruction::AShr)
                    {
                        ++NumAShrInst;
                    }
                    if (I.getOpcode() == Instruction::LShr)
                    {
                        ++NumLShrInst;
                    }
                    if (I.getOpcode() == Instruction::Shl)
                    {
                        ++NumShlInst;
                    }
                }
                if (isa<CallInst>(I))
                {
                    ++NumCallInst;
                    if (cast<CallInst>(I).getCalledFunction()->getReturnType()->isIntegerTy())
                    {
                        returnInt++;
                    }
                }
                if (isa<GetElementPtrInst>(I))
                {
                    ++NumGetElementPtrInst;
                }
                if (isa<LoadInst>(I))
                {
                    ++NumLoadInst;
                }
                if (isa<BitCastInst>(I))
                {
                    ++NumBitCastInst;
                }
                if (isa<ICmpInst>(I))
                {
                    ++NumICmpInst;
                }
                if (isa<SExtInst>(I))
                {
                    ++NumSExtInst;
                }
                if (isa<ZExtInst>(I))
                {
                    ++NumZExtInst;
                }
                if (isa<SelectInst>(I))
                {
                    ++NumSelectInst;
                }
                if (isa<AllocaInst>(I))
                {
                    ++NumAllocaInst;
                }
                if (isa<StoreInst>(I))
                {
                    ++NumStoreInst;
                }
                if (isa<UnaryInstruction>(I))
                {
                    testUnary++;
                }
                if (isa<BinaryOperator>(I))
                {
                    if (isa<Constant>(I.getOperand(0)) || isa<Constant>(I.getOperand(1)))
                    {
                        binaryConstArg++;
                    }
                }
                if (isFirst && isa<PHINode>(I))
                {
                    BeginPhi++;
                }
                if (isa<PHINode>(I))
                {
                    phiCount++;
                    unsigned inc = cast<PHINode>(I).getNumIncomingValues();
                    ArgsPhi += inc;
                    BBArgs += inc;
                }
                isFirst = false;
                tempCount++;
            }
            if (phiCount == 0)
            {
                BBNoPhi++;
            }
            else if (phiCount <= 3)
            {
                BB03Phi++;
            }
            else
            {
                BBHiPhi++;
            }
            if (BBArgs > 5)
            {
                BBNumArgsHi++;
            }
            else if (BBArgs >= 1)
            {
                BBNumArgsLo++;
            }
            if (tempCount < 15)
            {
                BlockLow++;
            }
            else if (tempCount <= 500)
            {
                BlockMid++;
            }
            else
            {
                BlockHigh++;
            }
        }
    }
    TotalMemInst += NumGetElementPtrInst + NumLoadInst + NumStoreInst + NumCallInst +
                    NumInvokeInst + NumAllocaInst;
    printStats();
    return false;
}

void Feature::getAnalysisUsage(AnalysisUsage &AU) const
{
    AU.setPreservesAll();
}

char Feature::ID = 0;
static RegisterPass<Feature> X("feature", "Feature Extraction", false, false);
static RegisterStandardPasses Y(PassManagerBuilder::EP_EarlyAsPossible, [](const PassManagerBuilder &Builder, legacy::PassManagerBase &PM)
                                { PM.add(new Feature()); });