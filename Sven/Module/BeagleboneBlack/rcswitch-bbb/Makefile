LDADD=-lrt -lpthread
PREFIX=/usr

all: test send livolo_send receive librcswitch.so

test: gpio.o
	gcc $(LDFLAGS) -O2 test.c gpio.o -o test $(LDADD)

send: RCSwitch.o gpio.o send.cpp
	$(CXX) $(CXXFLAGS) -O2 $(LDFLAGS) send.cpp gpio.o RCSwitch.o -o send $(LDADD)

livolo_send: gpio.o livolo_send.cpp livolo.cpp RCSwitch.o
	$(CXX) $(CXXFLAGS) -O2 $(LDFLAGS) livolo_send.cpp livolo.cpp gpio.o RCSwitch.o -o livolo_send $(LDADD)

receive: RCSwitch.o gpio.o receive.cpp
	$(CXX) $(CXXFLAGS) -O2 $(LDFLAGS) receive.cpp gpio.o RCSwitch.o -o receive $(LDADD)

librcswitch.so: RCSwitch.o gpio.o
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -shared -o librcswitch.so RCSwitch.o gpio.o

RCSwitch.o: RCSwitch.cpp
	$(CXX) $(CXXFLAGS) -O2 -fPIC -c RCSwitch.cpp

gpio.o: gpio.c
	gcc -c -O2 -fPIC gpio.c

clean:
	rm -rf *.o test send receive

install: librcswitch.so
	install *.so $(PREFIX)/lib
	
.PHONY: install clean
