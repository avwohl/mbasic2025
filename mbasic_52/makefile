
SOURCES= \
 bintrp.mac \
 biedit.mac \
 bimisc.mac \
 binlin.mac \
 bio.mac \
 biprtu.mac \
 biptrg.mac \
 bistrs.mac \
 dcpm.mac \
 dskcom.mac \
 f4.mac \
 fivdsk.mac \
 fiveo.mac \
 init.mac

OBJECTS = $(SOURCES:.mac=.rel)
TARGET = mbasic52.com

all: $(TARGET)

clean:	.
	@rm -f *.rel *.prn *.sym $(TARGET) *~ *.com

# Rule to link object files into the executable                                                  
$(TARGET): $(OBJECTS)
	ul80 -s $(OBJECTS) -o $(TARGET)

# Pattern rule to compile .cc files into .o object files                                # $< is the first dependency (the .cc file)                                             # $@ is the target (the .o file)                                                                 
%.rel: %.mac
	um80 -o $@ -l $*.prn $<
