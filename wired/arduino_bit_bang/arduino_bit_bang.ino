// Bit bang the signal using an output pin. This probably outputs the inverted signal and the timings might not match my
// latest measurements; good enough as PoC until I figure out how to drive the signal wire to low.
//
// There's no accuracy difference between using the actual arduino timers or using micros(). arduino-timer.h uses
// micros() under the hood, more convenient than actual timers.
#include <arduino-timer.h>

const unsigned long US = 1ul; // time dilation for debugging. No higher than 10ul or at least <100ul as we overflow otherwise
const unsigned long MS = 1000 * US;
const int SIGNAL_PIN = 7;                    // Digital pin with the least amount of features, in case I fry it
const uint8_t SIGNAL_LEVELS[] = {LOW, HIGH}; // need to be able to grab a pointer to it
const uint8_t* SIGNAL_LOW = &SIGNAL_LEVELS[0];
const uint8_t* SIGNAL_HIGH = &SIGNAL_LEVELS[1];
const unsigned int SIGNAL_LENGTHS[] = {466 * US, 1200 * US};

enum Action : unsigned char {
    UP,
    NOOP,
    DOWN
};

const unsigned char FRAME_SIZE = 12;
Timer<FRAME_SIZE * 2 + 1, micros> timer;
Action veluxAction = Action::UP;

bool maybeScheduleFrame(void*) {
    static unsigned char tick = 0;
    // Time per 'tick' is 10 ms. A frame takes 20 ms. Frames are sent in pairs.
    // Time between frames in a pair is 30 ms. Time between pairs is 60ms
    // (measured 64ms but hopefully close enough).
    if (tick == 13) {
        tick = 0;
    }
    if (tick == 0 || tick == 5) {
        scheduleFrame();
    }
    tick++;
    return true;
}

void scheduleFrame() {
    uint8_t c = 10;
    const bool PREAMBLE[] = {true, false, true, true, false, false};
    // Start with an offset to give us plenty of time to set up the timers, otherwise we chop off the first part of the signal
    unsigned long schedulingOffset = 1 * MS;
    for (bool bit : PREAMBLE) {
        scheduleBit(bit, schedulingOffset);
    }
    scheduleBit(false, schedulingOffset);                       // down velux 3
    scheduleBit(veluxAction == Action::DOWN, schedulingOffset); // down velux 1
    scheduleBit(false, schedulingOffset);                       // down velux 2
    scheduleBit(false, schedulingOffset);                       // up velux 2
    scheduleBit(veluxAction == Action::UP, schedulingOffset);   // up velux 1
    scheduleBit(false, schedulingOffset);                       // up velux 3
}

void scheduleBit(bool bit, unsigned long& offset) {
    scheduleSignal(SIGNAL_HIGH, SIGNAL_LENGTHS[bit], offset);
    scheduleSignal(SIGNAL_LOW, SIGNAL_LENGTHS[!bit], offset);
}

void scheduleSignal(const uint8_t* signal_level, unsigned long duration, unsigned long& offset) {
    timer.in(offset, setSignal, (void*)signal_level);
    offset += duration;
}

bool setSignal(void* high) {
    digitalWrite(SIGNAL_PIN, *(uint8_t*)high);
    return false;
}

void setup() {
    pinMode(SIGNAL_PIN, OUTPUT);
    timer.every(10 * MS, maybeScheduleFrame);
}

void loop() {
    // Doesn't actually tick a clock, it just compares task due times against current micros()
    timer.tick();
}
