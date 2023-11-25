import board
import pwmio
import digitalio
from time import monotonic
from time import sleep
from random import randrange
from random import uniform

btnBright = digitalio.DigitalInOut(board.D10)
btnBright.direction = digitalio.Direction.INPUT
btnBright.pull = digitalio.Pull.UP
btnMode = digitalio.DigitalInOut(board.D11)
btnMode.direction = digitalio.Direction.INPUT
btnMode.pull = digitalio.Pull.UP
swColor = digitalio.DigitalInOut(board.D12)
swColor.direction = digitalio.Direction.INPUT
swColor.pull = digitalio.Pull.UP
maxBright = 65530
xmasR = [maxBright, 0, 0, maxBright]
xmasG = [0, 0, maxBright, maxBright]
xmasB = [0, maxBright, 0, maxBright]
pwmRcol = 0
pwmGcol = 0
pwmBcol = 0
pwmR = pwmio.PWMOut(board.A2)
pwmG = pwmio.PWMOut(board.A3)
pwmB = pwmio.PWMOut(board.A4)


def updateMode():
    global mode
    if mode == 3:
        mode = 0
        sleep(0.5)
    else:
        mode = mode + 1
        sleep(0.5)

def updateBright():
    global maxBright
    global xmasR
    global xmasG
    global xmasB
    if maxBright - 10000 <= 0:
        maxBright = 65530
        xmasR = [maxBright, 0, 0, maxBright]
        xmasG = [0, 0, maxBright, maxBright]
        xmasB = [0, maxBright, 0, maxBright]
        sleep(0.5)
    else:
        maxBright = maxBright - 10000
        xmasR = [maxBright, 0, 0, maxBright]
        xmasG = [0, 0, maxBright, maxBright]
        xmasB = [0, maxBright, 0, maxBright]
        sleep(0.5)

def colorsUpdate():
    if activeColors == "xmas":
        xmasColors()
    else:
        rndColors()


def rndColors():
    global pwmRcol
    global pwmGcol
    global pwmBcol
    global maxBright
    rndStep = randrange(100, 10000, 10)
    pwmRcol = randrange(0, maxBright, rndStep)
    rndStep = randrange(100, 10000, 10)
    pwmGcol = randrange(0, maxBright, rndStep)
    rndStep = randrange(100, 10000, 10)
    pwmBcol = randrange(0, maxBright, rndStep)


def xmasColors():
    global pwmRcol
    global pwmGcol
    global pwmBcol
    global currXmas
    currXmas = randrange(0, 4, 1)
    pwmRcol = xmasR[currXmas]
    pwmGcol = xmasG[currXmas]
    pwmBcol = xmasB[currXmas]


def fadeStepper(curr, pwm):
    global newCurr
    if curr == pwm:
        pass
    elif curr - pwm > 0:
        curr = curr - 10
    else:
        curr = curr + 10
    newCurr = curr
    return (newCurr)


def blinkMode():
    global modeDur
    blinkOnDur = randrange(1, 6, 2)
    if pwmR.duty_cycle > 0 or pwmG.duty_cycle > 0 or pwmB.duty_cycle > 0:
        modeDur = 0.5
        setDutyCycles(0, 0, 0)
    else:
        modeDur = blinkOnDur
        colorsUpdate()
        setDutyCycles(pwmRcol, pwmGcol, pwmBcol)


def fadeMode(ran):
    global modeDur
    modeDur = 1
    if not ran:
        colorsUpdate()
        setDutyCycles(pwmRcol, pwmGcol, pwmBcol)
    currRcol = pwmRcol
    currGcol = pwmGcol
    currBcol = pwmBcol
    colorsUpdate()
    fadeDone = False
    while not fadeDone:
        btnCheck()
        if pwmRcol != currRcol:
            fadeStepper(currRcol, pwmRcol)
            currRcol = newCurr
        elif pwmGcol != currGcol:
            fadeStepper(currGcol, pwmGcol)
            currGcol = newCurr
        elif pwmBcol != currBcol:
            fadeStepper(currBcol, pwmBcol)
            currBcol = newCurr
        else:
            fadeDone = True
        setDutyCycles(currRcol, currGcol, currBcol)


def twinkleMode():
    global modeDur
    global maxBright
    global pwmRcol
    global pwmGcol
    global pwmBcol
    now = monotonic()
    lastRun = now
    lastTwinkle = now
    twinkleDelay = uniform(0, 1)
    modeDur = randrange(1, 10, 2)
    colorsUpdate()
    pwmRcol = int(pwmRcol - pwmRcol / 5)
    pwmGcol = int(pwmGcol - pwmGcol / 5)
    pwmBcol = int(pwmBcol - pwmBcol / 5)
    setDutyCycles(pwmRcol, pwmGcol, pwmBcol)
    currRcol = pwmRcol
    currGcol = pwmGcol
    currBcol = pwmBcol
    while True:
        now = monotonic()
        btnCheck()
        if now <= twinkleDelay + lastTwinkle:
            pass
        else:
            twinkleDelay = uniform(0, 1)
            setDutyCycles(maxBright, maxBright, maxBright)
            sleep(.1)
            setDutyCycles(currRcol, currGcol, currBcol)
            lastTwinkle = now
        if now >= modeDur + lastRun:
            break


def setDutyCycles(r, g, b):
    pwmR.duty_cycle = r
    pwmG.duty_cycle = g
    pwmB.duty_cycle = b


def btnCheck():
    if not btnMode.value:
        updateMode()
    elif not btnBright.value:
        updateBright()
    else:
        return


def main():
    global activeColors
    global modeDur
    global lastRun
    global ran
    lastRun = -1
    modeDur = 0
    ran = False
    while True:
        now = monotonic()
        btnCheck()
        if now >= modeDur + lastRun:
            if swColor.value:
                activeColors = "xmas"
            else:
                activeColors = "rnd"
            if mode == 0:
                blinkMode()
            elif mode == 1:
                fadeMode(ran)
                ran = True
            elif mode == 2:
                twinkleMode()
            elif mode == 3:
                # all
                rndMode = randrange(0, 2, 1)
                if rndMode == 0:
                    blinkMode()
                elif rndMode == 1:
                    fadeMode(ran)
                    ran = True
                elif rndMode == 2:
                    twinkleMode()
            lastRun = now


mode = 1
main()
