import random

class art:
    # http://www.glassgiant.com/ascii/
    # Max Width: 40 characters
    lifting = """
                    ~  I                
                      : O               
                     \, \               
                     |  |               
                     |  |               
  ?ZZZ$$D~           ZOZ8     Z$Z$ZZD,  
 7ZZ$Z$DDD+        ,IIIII+   I$ZZZZDD8  
 Z8Z$ZND7+IIII=     I~+IIDII8Z8$OZDDDDI 
 ?8ZDZDIIIIIIII  Z$IIIIIZIIIO$O$DZN88NN 
$Z8ZDZDIIIIOIIIIIIIIIIIIIII$O$ZZOZND8DI 
 Z8Z8ZND7III77INIIIIIIIIIZ7ZNZ8Z8$DDDD  
 8ZZZZ$DIIII$IZ7IIIIIIIII7IIIZZZZZZ8DD  
  ?OOZ8OZ7I8II7ZIIIIIIIIIDIIII8OZZZZ8   
         $ZII7 ~IIIIIIIIII7II7O         
           ZI   IIIIIIIII$ZIDI?         
                7I7IIIIIIIIII7          
                 7IIIIIIIIII7+          
                  7IIIIIIIII8           
                   ZIII7IIIIN87$ZD      
                    8$7$$$7$8D8Z~       
                      $Z7IO7O78,        
                      $,  8             
                      ,~  O             
                         :8             
    """

    posing = """                  
                       N                
                                        
                        N               
                    78                  
                   +D? D                
                 $$IIZ$                 
                 ZD$$ZI                 
              8O8IIIIII7O               
            OI777IIIIIIIII$8            
      N7$8DNIIIIIIIIIIIIIIIII7OD8       
     OIZO  ZIIIIIIIIIIIIIII$D  NZIZ     
   N7IIOI  $IIIIIIIIIIIIII87   I$II     
 $~IIIIIID  IIIIIIIIIIIIII$D  DIII77    
OI~IIIIIIIZ IIIIIIII7$7$I8$  OIIIIII7   
IIIIIII III $II7IIIIIIII?$  IIIDIII=II  
OIIIIII IIN  IIIIIIIIIIID$  II  III~~~7 
 7IIIII      DIII7$7IIII$N   Z  IIIIIID 
   DIII       OII$777III$D77ON NIIIII7  
               NO$ZO8O$O?$OZO  IIIII    
                  8$$Z7O$$8             
                 IN  N8$                
                  I   O                 
                      $I                
    """

    pictures = [lifting, posing]

    @staticmethod
    def getArt():
        index = random.randint(0, len(art.pictures) - 1)
        return art.pictures[index]
