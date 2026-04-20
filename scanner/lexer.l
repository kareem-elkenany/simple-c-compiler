%{ 
    
    #include <stdio.h>

    /* REQUIRED: Definitions so the compiler knows what these words mean */
    #define EOL 1
    #define IF 2
    #define ELSE 3
    #define WHILE 4
    #define OPENBRACE 5
    #define CLOSEBRACE 6
    #define LEFTPAREN 7
    #define RIGHTPAREN 8
    #define ASSIGN 9
    #define EQUAL 10
    #define LESSTHAN 11
    #define GREATERTHAN 12
    #define LESSOREQUAL 13
    #define GREATEROREQUAL 14
    #define IDENTIFIER 15
    #define NUMBER 16
    #define STRING 17
    #define PRINT 18
    #define READ 19
    #define PLUS 20
    #define MINUS 21
    #define MULTIPLICATION 22
    #define DIVISION 23

    FILE *tokenFile;
%}

/*ignore case for all rules */
%option caseless
%option yylineno

/* 1. EOL Handling: Collapse newlines and ignore trailing spaces */
EOL ([ \t]*\n)+
IF "if"
ELSE "else"
WHILE "while"
OPENBRACE "{"
CLOSEBRACE "}"
LEFTPAREN "("
RIGHTPAREN ")"
ASSIGN "is"
EQUAL "equal"
LESSOREQUAL "less than or equal"
GREATEROREQUAL "greater than or equal"
LESSTHAN "less than"
GREATERTHAN "greater than"
IDENTIFIER [a-zA-Z](_[a-zA-Z0-9]|[a-zA-Z0-9])*
NUMBER [0-9]+
STRING \"[^\"]*\"
PRINT "show"
READ "read"
PLUS "plus"
MINUS "minus"
MULTIPLICATION "multiplied by"
DIVISION "divided by"
WHITESPACE [ \t]+

%%
{EOL} { 
        fprintf(tokenFile, "(\\n, EOL)\n"); 
        printf("(\\n, EOL)\n"); 
        return EOL; 
      }

        /* 2. RULES SECTION - Longest matches MUST come first to avoid warnings */
        /* Multi-word operators first */

{LESSOREQUAL} { 
        fprintf(tokenFile, "(%d, %s, LESSOREQUAL)\n", yylineno, yytext); 
        printf("(%d, %s, LESSOREQUAL)\n", yylineno, yytext); 
        return LESSOREQUAL; 
      }

{GREATEROREQUAL} { 
        fprintf(tokenFile, "(%d, %s, GREATEROREQUAL)\n", yylineno, yytext); 
        printf("(%d, %s, GREATEROREQUAL)\n", yylineno, yytext); 
        return GREATEROREQUAL; 
      }

{MULTIPLICATION} { 
        fprintf(tokenFile, "(%d, %s, MULTIPLICATION)\n", yylineno, yytext); 
        printf("(%d, %s, MULTIPLICATION)\n", yylineno, yytext); 
        return MULTIPLICATION; 
      }

{DIVISION} { 
        fprintf(tokenFile, "(%d, %s, DIVISION)\n", yylineno, yytext); 
        printf("(%d, %s, DIVISION)\n", yylineno, yytext); 
        return DIVISION; 
      }

        /* the shorter phrases */

{LESSTHAN} { 
        fprintf(tokenFile, "(%d, %s, LESSTHAN)\n", yylineno, yytext); 
        printf("(%d, %s, LESSTHAN)\n", yylineno, yytext); 
        return LESSTHAN; 
      }

{GREATERTHAN} { 
        fprintf(tokenFile, "(%d, %s, GREATERTHAN)\n", yylineno, yytext); 
        printf("(%d, %s, GREATERTHAN)\n", yylineno, yytext); 
        return GREATERTHAN; 
      }

        /* Keywords and Braces */

{IF} { 
        fprintf(tokenFile, "(%d, %s, IF)\n", yylineno, yytext); 
        printf("(%d, %s, IF)\n", yylineno, yytext); 
        return IF; 
      }

{ELSE} { 
        fprintf(tokenFile, "(%d, %s, ELSE)\n", yylineno, yytext); 
        printf("(%d, %s, ELSE)\n", yylineno, yytext); 
        return ELSE; 
      }

{WHILE} { 
        fprintf(tokenFile, "(%d, %s, WHILE)\n", yylineno, yytext); 
        printf("(%d, %s, WHILE)\n", yylineno, yytext); 
        return WHILE; 
      }

{PRINT} {
        fprintf(tokenFile, "(%d, %s, PRINT)\n", yylineno, yytext);
        printf("(%d, %s, PRINT)\n", yylineno, yytext);
        return PRINT;
        }

{READ} {
        fprintf(tokenFile, "(%d, %s, READ)\n", yylineno, yytext);
        printf("(%d, %s, READ)\n", yylineno, yytext);
        return READ;
        }

{OPENBRACE} { 
        fprintf(tokenFile, "(%d, %s, OPENBRACE)\n", yylineno, yytext); 
        printf("(%d, %s, OPENBRACE)\n", yylineno, yytext); 
        return OPENBRACE; 
      }

{CLOSEBRACE} { 
        fprintf(tokenFile, "(%d, %s, CLOSEBRACE)\n", yylineno, yytext); 
        printf("(%d, %s, CLOSEBRACE)\n", yylineno, yytext); 
        return CLOSEBRACE; 
      }

{LEFTPAREN} { 
        fprintf(tokenFile, "(%d, %s, LEFTPAREN)\n", yylineno, yytext); 
        printf("(%d, %s, LEFTPAREN)\n", yylineno, yytext); 
        return LEFTPAREN; 
      }

{RIGHTPAREN} { 
        fprintf(tokenFile, "(%d, %s, RIGHTPAREN)\n", yylineno, yytext); 
        printf("(%d, %s, RIGHTPAREN)\n", yylineno, yytext); 
        return RIGHTPAREN;
        }

{ASSIGN} {
        fprintf(tokenFile, "(%d, %s, ASSIGN)\n", yylineno, yytext);
        printf("(%d, %s, ASSIGN)\n", yylineno, yytext);
        return ASSIGN;
        }

{EQUAL} {
        fprintf(tokenFile, "(%d, %s, EQUAL)\n", yylineno, yytext);
        printf("(%d, %s, EQUAL)\n", yylineno, yytext);
        return EQUAL;
        }

{PLUS} {
        fprintf(tokenFile, "(%d, %s, PLUS)\n", yylineno, yytext);
        printf("(%d, %s, PLUS)\n", yylineno, yytext);
        return PLUS;
        }

{MINUS} {
        fprintf(tokenFile, "(%d, %s, MINUS)\n", yylineno, yytext);
        printf("(%d, %s, MINUS)\n", yylineno, yytext);
        return MINUS;
        }

{IDENTIFIER} {
        fprintf(tokenFile, "(%d, %s, IDENTIFIER)\n", yylineno, yytext);
        printf("(%d, %s, IDENTIFIER)\n", yylineno, yytext);
        return IDENTIFIER;
        }

{NUMBER} {
        fprintf(tokenFile, "(%d, %s, NUMBER)\n", yylineno, yytext);
        printf("(%d, %s, NUMBER)\n", yylineno, yytext);
        return NUMBER;
        }

{STRING} {
        fprintf(tokenFile, "(%d, %s, STRING)\n", yylineno, yytext);
        printf("(%d, %s, STRING)\n", yylineno, yytext);
        return STRING;
        }


{WHITESPACE} { /* ignore whitespace */ }

. { printf("Error on line %d: Unexpected character '%s'\n", yylineno, yytext); }

%%

int yywrap() {
    return 1; // No more input
}

int main(int argc, char **argv) {
    // 1. Open your code snippet
    // We should change this when GUI is built, but for now we will just read from a file called input.txt
    FILE *inputFile = fopen("input.txt", "r");
    if (!inputFile) {
        printf("Error: input.txt not found!\n");
        return 1;
    }

    // 2. Open the file where you will save the tokens
    tokenFile = fopen("tokens.txt", "w");
    if (!tokenFile) {
        printf("Error: Could not create tokens.txt!\n");
        fclose(inputFile);
        return 1;
    }

    yyin = inputFile;
    
    // 3. Process the file until end, will stop when yylex returns 0 (EOF)
    while (yylex() != 0);


    fclose(inputFile);
    fclose(tokenFile);
    
    return 0;
}