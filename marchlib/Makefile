# Target library
objs := march.o
programs := pymarch.x

CC = gcc
ifneq ($(S),1)
LIBBUILD := ar rcs
lib := libmarch.a
else
LIBBUILD := gcc -shared -o
lib := libmarch.so
endif

targets := $(lib)

ifneq ($(S),1)
targets += $(programs)
endif

CFLAGS := -Wall -Werror
ifneq ($(D),1)
CFLAGS += -O2
else
CFLAGS += -O0
CFLAGS += -g
endif

ifeq ($(S),1)
CFLAGS += -fPIC
else
XFLAGS := -lm -lpthread
endif

all: $(targets)

deps := $(patsubt %.o,%.d,$(objs))
-include $(deps)
DEPFLAGS = -MMD -MF $(@:.o=.d)

$(lib): $(objs)
	$(LIBBUILD) $@ $(objs) $(LDFLAGS)

%.x: %.c
	$(CC) $(CFLAGS) -o $@ $< $(lib) $(XFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $< $(DEPFLAGS)

clean:
	rm -rf $(targets) $(objs) $(deps) $(lib) *.d
