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
        fprintf(tokenFile, "(%s, LESSOREQUAL)\n", yytext); 
        printf("(%s, LESSOREQUAL)\n", yytext); 
        return LESSOREQUAL; 
      }

{GREATEROREQUAL} { 
        fprintf(tokenFile, "(%s, GREATEROREQUAL)\n", yytext); 
        printf("(%s, GREATEROREQUAL)\n", yytext); 
        return GREATEROREQUAL; 
      }

{MULTIPLICATION} { 
        fprintf(tokenFile, "(%s, MULTIPLICATION)\n", yytext); 
        printf("(%s, MULTIPLICATION)\n", yytext); 
        return MULTIPLICATION; 
      }

{DIVISION} { 
        fprintf(tokenFile, "(%s, DIVISION)\n", yytext); 
        printf("(%s, DIVISION)\n", yytext); 
        return DIVISION; 
      }

        /* the shorter phrases */

{LESSTHAN} { 
        fprintf(tokenFile, "(%s, LESSTHAN)\n", yytext); 
        printf("(%s, LESSTHAN)\n", yytext); 
        return LESSTHAN; 
      }

{GREATERTHAN} { 
        fprintf(tokenFile, "(%s, GREATERTHAN)\n", yytext); 
        printf("(%s, GREATERTHAN)\n", yytext); 
        return GREATERTHAN; 
      }

        /* Keywords and Braces */

{IF} { 
        fprintf(tokenFile, "(%s, IF)\n", yytext); 
        printf("(%s, IF)\n", yytext); 
        return IF; 
      }

{ELSE} { 
        fprintf(tokenFile, "(%s, ELSE)\n", yytext); 
        printf("(%s, ELSE)\n", yytext); 
        return ELSE; 
      }

{WHILE} { 
        fprintf(tokenFile, "(%s, WHILE)\n", yytext); 
        printf("(%s, WHILE)\n", yytext); 
        return WHILE; 
      }

{PRINT} {
        fprintf(tokenFile, "(%s, PRINT)\n", yytext);
        printf("(%s, PRINT)\n", yytext);
        return PRINT;
        }

{READ} {
        fprintf(tokenFile, "(%s, READ)\n", yytext);
        printf("(%s, READ)\n", yytext);
        return READ;
        }

{OPENBRACE} { 
        fprintf(tokenFile, "(%s, OPENBRACE)\n", yytext); 
        printf("(%s, OPENBRACE)\n", yytext); 
        return OPENBRACE; 
      }

{CLOSEBRACE} { 
        fprintf(tokenFile, "(%s, CLOSEBRACE)\n", yytext); 
        printf("(%s, CLOSEBRACE)\n", yytext); 
        return CLOSEBRACE; 
      }

{LEFTPAREN} { 
        fprintf(tokenFile, "(%s, LEFTPAREN)\n", yytext); 
        printf("(%s, LEFTPAREN)\n", yytext); 
        return LEFTPAREN; 
      }

{RIGHTPAREN} { 
        fprintf(tokenFile, "(%s, RIGHTPAREN)\n", yytext); 
        printf("(%s, RIGHTPAREN)\n", yytext); 
        return RIGHTPAREN;
        }

{ASSIGN} {
        fprintf(tokenFile, "(%s, ASSIGN)\n", yytext);
        printf("(%s, ASSIGN)\n", yytext);
        return ASSIGN;
        }

{EQUAL} {
        fprintf(tokenFile, "(%s, EQUAL)\n", yytext);
        printf("(%s, EQUAL)\n", yytext);
        return EQUAL;
        }

{PLUS} {
        fprintf(tokenFile, "(%s, PLUS)\n", yytext);
        printf("(%s, PLUS)\n", yytext);
        return PLUS;
        }

{MINUS} {
        fprintf(tokenFile, "(%s, MINUS)\n", yytext);
        printf("(%s, MINUS)\n", yytext);
        return MINUS;
        }

{IDENTIFIER} {
        fprintf(tokenFile, "(%s, IDENTIFIER)\n", yytext);
        printf("(%s, IDENTIFIER)\n", yytext);
        return IDENTIFIER;
        }

{NUMBER} {
        fprintf(tokenFile, "(%s, NUMBER)\n", yytext);
        printf("(%s, NUMBER)\n", yytext);
        return NUMBER;
        }

{STRING} {
        fprintf(tokenFile, "(%s, STRING)\n", yytext);
        printf("(%s, STRING)\n", yytext);
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






