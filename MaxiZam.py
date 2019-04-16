
import re

# expression reguliere pour identifier un label 
lab = r'^[A-Z]*(.)+:$'


class MLValue:
    MLtrue = 1
    MLfalse = 0
    MLunit = 0
        
    def __init__(self):
        self.value = None
        
    def __repr__(self):
        if self.value is MLValue.MLtrue:
            return "1"
        if self.value is MLValue.MLfalse:
            return "0"
        if self.value is MLValue.MLunit:
            return "()"
        return str(self.value)

    
class MLInt(MLValue):

    def __init__(self, val):
        self.value = val


class MLClosure(MLValue):

    def __init__(self, pc, env):
        self.value = (pc, env)

        
class MLBlock(MLValue):

    def __init__(self, block):
        self.value = block
    

class MaxiZam:

    def __init__(self, fileName):
        # ======================== Registres =====================#
        self.prog = list()
        self.stack = list()
        self.env = list()
        self.pc = 0
        self.accu = ""  # On ne peut pas mettre () puisque cette valeur vaut 0
        self.extra_args = 0
        self.trap_sp = -99999
        # ========================================================#
        # ============== Initialisation de la machine ============#
        f = open(fileName, "r")
        listeResult = list()
        for line in f:
            listeResult.append(line[:-1])
        for a in listeResult:
            self.prog.append(a.split())
        self.apptermOpti()

        # =========================================================# 
    def apptermOpti(self):
        cpt = 0
        for i in range(len(self.prog) - 1):
            if((self.prog[i][0] == "APPLY")and(self.prog[i + 1][0] == "RETURN")):
                cpt += 1
                n = int(self.prog[i][1])
                m = int(self.prog[i + 1][1])
                m += n
                self.prog[i][0] = "APPTERM"
                self.prog[i][1] = str(n) + "," + str(m)
                for a in range(i + 1, len(self.prog) - 1):
                    self.prog[a] = self.prog[a + 1] 
        
    def position(self, L):
        if(type(L) == int):
            return L
        cpt = 0
        for p in self.prog:
            if(re.match(lab, p[0])):
                if(L == p[0][:-1]):
                    return cpt
            cpt += 1
        return -1
        
    def treat(self, inst):
        print("pc : " + str(self.pc) + " accu : " + str(self.accu) + " env : " + str(self.env) + " stack : " + str(self.stack) + " extra_args : " + str(self.extra_args) + " trap_sp : " + str(self.trap_sp))
        print("--------" + str(self.prog[self.pc]) + "----------")
        if(re.match(lab, inst[0])):
            self.MySwitch(inst[1], inst[1:])
        else:
            self.MySwitch(inst[0], inst)
    
    def compute(self):
        print("DEBUT DE L'EXECUTION")
        while len(self.prog)>0:
            self.treat(self.prog[self.pc])
                
    def MySwitch(self, op, inst):
        if(op == "CONST"):
            return self.CONST(inst)
        if(op == "PRIM"):
            return self.PRIM(inst)
        if(op == "BRANCH"):
            return self.BRANCH(inst)
        if(op == "BRANCHIFNOT"):
            return self.BRANCHIFNOT(inst)
        if(op == "PUSH"):
            return self.PUSH()
        if(op == "POP"):
            return self.POP()
        if(op == "ACC"):
            return self.ACC(inst)
        if(op == "ENVACC"):
            return self.ENVACC(inst)
        if(op == "CLOSURE"):
            return self.CLOSURE(inst)
        if(op == "APPLY"):
            return self.APPLY(inst)
        if(op == "RETURN"):
            return self.RETURN(inst)
        if(op == "STOP"):
            return self.STOP()
        if(op == "CLOSUREREC"):
            return self.CLOSUREREC(inst)
        if(op == "OFFSETCLOSURE"):
            return self.OFFSETCLOSURE(inst)
        if(op == "GRAB"):
            return self.GRAB(inst)
        if(op == "RESTART"):
            return self.RESTART()
        if(op == "APPTERM"):
            return self.APPTERM(inst)
        if(op == "MAKEBLOCK"):
            return self.MAKEBLOCK(inst)
        if(op == "GETFIELD"):
            return self.GETFIELD(inst)
        if(op == "VECTLENGTH"):
            return self.VECTLENGTH()
        if(op == "GETVECTITEM"):
            return self.GETVECTITEM()
        if(op == "SETFIELD"):
            return self.SETFIELD(inst)
        if(op == "SETVECTITEM"):
            return self.SETVECTITEM()
        if(op == "ASSIGN"):
            return self.ASSIGN(inst)
        if(op == "PUSHTRAP"):
            return self.PUSHTRAP(inst)
        if(op == "POPTRAP"):
            return self.POPTRAP()
        if(op == "RAISE"):
            return self.RAISE()
    
    def STOP(self):
        print("FIN D'EXECUTION")
        print("VALEUR CALCULEE : " + str(self.accu))
        self.prog = list()

    def CONST(self, inst):
        self.accu = MLInt(int(inst[1]))
        self.pc += 1
        self.treat(self.prog[self.pc])
        
    def PRIM(self , inst):
        op = inst[1]
        if(op == "+"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            tmp = a + x
            self.accu = MLInt(tmp)
            self.pc += 1
        if(op == "-"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            tmp = x - a
            self.accu = MLInt(tmp)
            self.pc += 1
        if(op == "/"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            tmp = a // x
            self.accu = MLInt(tmp)
            self.pc += 1
        if(op == "*"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            tmp = a * x
            self.accu = MLInt(tmp)
            self.pc += 1
        if(op == "or"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(a == MLfalse):
                a = ""
            if(x == MLValue.MLfalse):
                x = ""
            if(bool(a) or bool(x)):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "and"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(a == MLValue.MLfalse):
                a = ""
            if(x == MLValue.MLfalse):
                x = ""
            if(bool(a) and bool(x)):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "<>"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(a != x):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "="):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(a == x):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "<"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(x < a):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == ">"):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(x > a):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "<="):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(x <= a):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == ">="):
            a = self.stack.pop(0).value
            while(isinstance(a, MLValue)):
                a = a.value
            x = self.accu.value
            if(x >= a):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
        if(op == "not"):
            x = self.accu.value
            if(x == MLValue.MLfalse):
                self.accu = MLInt(MLValue.MLtrue)
            else:
                self.accu = MLInt(MLValue.MLfalse)
            self.pc += 1
            return self.treat(self.prog[self.pc])
        if(op == "print"):
            x = self.accu.value
            print(" PRINTING : " + str(x))
            self.pc += 1
        
    def BRANCH(self, inst):
        k = inst[1]
        self.pc = self.position(k)
    
    def BRANCHIFNOT(self, inst):
        if(self.accu.value == MLValue.MLfalse):
            k = inst[1]
            self.pc = self.position(k)
        else:
            self.pc += 1
    
    def PUSH(self):
        if(self.accu != ""):
            x = self.accu
            self.stack.insert(0, x)
        self.pc += 1
    
    def POP(self):
        if len(self.stack) > 0:
            self.stack.pop(0)
        self.pc += 1
    
    def ACC(self, inst):
        i = int(inst[1])
        if(len(self.stack) > i):
            tmp = self.stack[i]
            self.accu = tmp
        self.pc += 1
    
    def ENVACC(self, inst):
        i = int(inst[1])
        if(len(self.env) > i):
            tmp = self.env[i]
            self.accu = tmp
        self.pc += 1
    
    def CLOSURE(self, inst):
        a = inst[1].split(",")
        L = self.position(a[0])
        n = int(a[1])
        if(n > 0):
            self.stack.insert(0, self.accu)
        depil = list()
        for i in range(n):
            depil.append(self.stack.pop(0))
        self.accu = MLClosure(L, depil)
        self.pc += 1
        
    def RETURN(self, inst):
        n = int(inst[1])
        for i in range(n):
            self.stack.pop(0)
        if(self.extra_args == 0):
            self.pc = int(self.stack.pop(1).value)
            self.env = self.stack.pop(1)
            self.stack.pop(0)    
        else:
            self.extra_args -= 1
            self.pc = self.position(self.accu.value[0])
            self.env = self.accu.value[1]
    
    def APPLY(self, inst):
        n = int(inst[1])
        liste = list()
        if(len(self.stack) > n):
            for i in range(n):
                liste.append(self.stack.pop(0))
        self.stack.insert(0, self.env)
        self.stack.insert(0, MLInt(self.pc + 1))
        self.stack.insert(0, MLInt(self.extra_args))
        for i in range(len(liste)):
            self.stack.insert(0, liste[len(liste) - i - 1])
        self.env = (self.accu.value[1])
        self.pc = self.position(self.accu.value[0])
        self.extra_args = n - 1

    def CLOSUREREC(self, inst):
        a = inst[1].split(",")
        L = self.position(a[0])
        n = int(a[1])
        if(n > 0):
            self.stack.insert(0, self.accu)
        depil = list()
        depil.append(L)
        for i in range(n):
            depil.append(self.stack.pop(0))
        self.accu = MLClosure(L, depil)
        self.stack.insert(0, self.accu)
        self.pc += 1
    
    def OFFSETCLOSURE(self, inst):
        self.accu = MLClosure(self.env[0], self.env)
        self.pc += 1
    
    def GRAB(self, inst):
        n = int(inst[1])
        if(self.extra_args >= n):
            self.extra_args -= n
            self.pc += 1
        else:
            depil = list()
            c = self.pc
            e = self.env
            depil.append(e)
            for i in range(self.extra_args + 1):
                depil.append(self.stack.pop(0))
            self.accu = MLClosure(c - 1, depil)
            self.extra_args = self.stack.pop(0).value
            self.pc = self.stack.pop(0).value
            self.env = self.stack.pop(0)
        
    def RESTART(self):
        n = len(self.env)
        e = self.env[0]
        self.env.pop(0)
        for i in range(0, len(self.env)):
            self.stack.insert(0, self.env[len(self.env) - i - 1])
        self.env = e
        self.extra_args += (n - 1)
        self.pc += 1
    
    def APPTERM(self, inst):
        a = inst[1].split(",")
        n = int(a[0])
        m = int(a[1])        
        depil = list()
        for i in range(n):
            depil.append(self.stack.pop(0))
        local = list()
        for j in range(m - n):
            local.append(self.stack.pop(0))
        for i in range(n):
            self.stack.insert(0, depil[len(depil) - i - 1])
        self.pc = self.position(self.accu.value[0])
        self.env = self.accu.value[1]
        self.extra_args += (n - 1)
         
    def MAKEBLOCK(self, inst):
        n = int(inst[1])
        bloc = list()
        for i in range(n):
            if(i == 0):
                bloc.append(self.accu)
            else:
                bloc.append(self.stack.pop(0))
        self.accu = MLBlock(bloc)
        self.pc += 1
        
    def GETFIELD(self, inst):
        n = int(inst[1])
        v = self.accu.value[n].value      
        self.accu = MLInt(v)
        self.pc += 1
        
    def VECTLENGTH(self):
        self.accu = MLInt(len(self.accu.value))     
        self.pc += 1
        
    def GETVECTITEM(self):
        n = self.stack.pop(0).value
        self.accu = MLInt(self.accu.value[n])      
        self.pc += 1
        
    def SETFIELD(self, inst):
        n = int(inst[1])
        self.accu.value[n] = self.stack.pop(0)      
        self.pc += 1
        
    def SETVECTITEM(self):
        n = self.stack.pop(0).value
        v = self.stack.pop(0)
        self.accu.value[n] = v
        self.accu = MLInt(0)        
        self.pc += 1
        
    def ASSIGN(self, inst):
        n = int(inst[1])
        self.stack[n] = self.accu
        self.accu = MLInt(MLValue.MLfalse)
        self.pc += 1
        
    def PUSHTRAP(self, inst):
        L = self.position(inst[1])
        self.stack.insert(0, MLInt(self.extra_args))
        self.stack.insert(0, self.env)
        self.stack.insert(0, self.trap_sp)
        self.stack.insert(0, MLInt(L))
        self.trap_sp = self.stack[0]
        self.pc += 1
        
    def POPTRAP(self):
        self.stack.pop(0)
        self.trap_sp = self.stack.pop(0)
        self.stack.pop(0)
        self.stack.pop(0)
        self.pc += 1

    def RAISE(self):
        if(self.trap_sp == -99999):
            print("--------------Exception levée: ", self.trap_sp, " -----------")
            self.STOP()
        else:
            while(self.stack[0] is not self.trap_sp):
                self.stack.pop(0)
            self.pc = self.stack.pop(0).value
            self.trap_sp = self.stack.pop(0)
            self.env = self.stack.pop(0)
            self.extra_args = self.stack.pop(0).value


def UserFriendly():
    while(True):
        print ("Pour sortir saisir : quit")
        print ("Sinon veuillez saisir le chemin du fichier a executer : ")
        name = input()
        if(name == "quit"):
            print("au revoir")
            break
        try:
            open(name, 'r')
            m = MaxiZam(name)
            m.compute() 
        
        except IOError:
            print ("Je ne peux pas lire le fichier:", name)


# tests/rec_funs/facto.txt
UserFriendly()
