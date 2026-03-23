from collections import defaultdict

from game.handlers import rollbackYUp, rollbackXLeft, rollbackXRight
from game.overlap import OverlapResult, moverToMover, Result
from movers.blocks.block import Block, BlockChain
from movers.cloud import SpawnBlock
from movers.gate import Gate
from movers.interactive_mover import InteractiveMover
from movers.movers import Mover
from system.defs import Vertical, Facing, Id, Events, Move, PushAction


class InteractionListener:

    listeners = {}
    result = None
    expired = False
    direction = 0

    def __init__(self, mva, mvb, result):
        self.mva = mva
        self.mvb = mvb
        self.result = result

    def __str__(self):
        return "interaction: " + str(self.mva) + " " + str(self.mvb)

    def moverToCoilInteraction(self):
        
        ma : Mover = self.mva
        mb : Mover = self.mvb
        
        if not ma.xaccl and mb.xvel < mb.dash_xvel \
                or ma.xaccl < 0 and mb.xloc <= mb.default_xloc - 0xC:
            ma.interaction_events.append(Events.MOVER_RECOIL)
            mb.interaction_events.append(Events.MOVER_RECOIL)
        elif ma.hb.y0 > mb.hb.y1 \
            or ma.hb.y1 < mb.hb.y0:
            ma.interaction_events.append(Events.HALT_PUSHING)
            mb.interaction_events.append(Events.MOVER_RECOIL)
            self.expired = True
        else:
            if int(mb.xloc) != mb.default_xloc:
                InteractionListener.check_sides(self.result)
            else:
                if ma.xvel >= mb.MAX_XVEL_PUSH \
                        and ma.xaccl >= 0:
                    ma.interaction_events.append(Events.MOVER_LEAVE_COIL)
                    self.expired = True
                    mb.xaccl = 0
                    mb.xvel = 0
                    return
            self.moverToBlockInteraction()

    def moverToBlockInteraction(self):

        ma : Mover = self.mva
        mb : Mover = self.mvb

        if mb.move_state == Move.GOAL:
            ma.interaction_events.append(Events.HALT_PUSHING)
            self.expired = True
            return

        if mb.xaccl < 0:
            ma.xaccl = mb.xaccl

        if ma.xaccl < 0:
            mb.xaccl = ma.xaccl

        if not ma.xaccl \
        or ma.direction != mb.direction \
                or ma.hb.y0 > mb.hb.y1 \
                or ma.hb.y1 < mb.hb.y0:
                if ma.xaccl >= 0:
                    ma.interaction_events.append(Events.HALT_PUSHING)
                if mb.xaccl >= 0:
                    mb.interaction_events.append(Events.HALT_PUSHING)
                self.expired = True
                print("halt to pushing")
                return

        InteractionListener.check_sides(self.result)
        ma.interaction_events.append(Events.CONTINUE_PUSHING)
        mb.interaction_events.append(Events.CONTINUE_PUSHING)

        if mb.pcounterAction == PushAction.SHOVE:
            return

        if mb.id == Id.PLAYER.value:
            return

        ma.pcounter += 1
        if 2 == ma.pcounter:
            ma.xvel = ma.push_xvel
            mb.xvel = mb.push_xvel
        if ma.pcounter >= 0x20:
            ma.interaction_events.append(Events.HALT_PUSHING)
            mb.interaction_events.append(Events.PUSH_TO_SKID)
            mb.interaction_events.remove(Events.CONTINUE_PUSHING)
            self.expired = True
            ma.pcounter = 0

    def blockToDisposal(self, nodes = []):
        ma: Mover = self.mva
        mb: Mover = self.mvb

        ma.snap_xloc = mb.xloc
        ma.direction = Facing.LEFT if ma.xloc > mb.xloc else Facing.RIGHT
        ma.xvel = 0.5
        ma.xaccl = 0.0
        ma.move_state = Move.GOAL
        self.expired = True

    interactions = defaultdict(lambda : InteractionListener.moverToBlockInteraction,
                               {Id.SIDECOIL.value : moverToCoilInteraction,
                                Id.DISPOSAL.value : blockToDisposal})

    @classmethod
    def evalInteractions(cls):
        out = ""
        for listener in cls.listeners.values():
            key = listener.mvb.id
            interaction = cls.interactions[key]
            interaction(listener)
            out += str(listener) + "\n"

        # delete dict entry without exception
        cls.listeners = dict(filter(lambda x: not x[1].expired, cls.listeners.items()))
        return out

    @classmethod
    def initInteraction(self, ma : InteractiveMover, mb : InteractiveMover,
                        result : OverlapResult):
        uuida = ma.auuid
        uuidb = mb.auuid

        if mb.id == Id.RAMP.value:
            if ma.id in (Id.BLOCK.value, Id.BLOCKCHAIN.value):
                #if ma.xaccl < 0:
                #    ma.set_jump(1.25)
                return False

        if ma.id == Id.PLAYER.value and mb.id in (\
                Id.DISPOSAL.value, Id.RAMP.value):
            return True if mb.id == Id.DISPOSAL.value else False

        if (uuida, uuidb) in InteractionListener.listeners.keys():
            return True

        if not ma.xvel and not mb.xvel:
            return True

        if not mb.base_xaccl:
            return True

        InteractionListener.listeners[(uuida, uuidb)] = \
            InteractionListener(result.mva, result.mvb, result)

        if mb.id == Id.DISPOSAL.value:
            if ma.id == Id.BLOCK.value:
                return False
            return True

        if mb.xvel >= ma.MAX_XVEL_WALK:
            direction = mb.direction
            if not mb.xaccl:
                xaccl = mb.base_xaccl / 8.0
            else:
                xaccl = mb.xaccl
            friction = ma.friction
            xvel = mb.xvel
        else:
            if ma.xaccl < 0:
                mb.pcounterAction = PushAction.SHOVE
            else:
                mb.pcounterAction = mb.defaultPushAction

            direction = ma.direction
            if ma.xaccl >= 0:
                friction = mb.friction
                xaccl = ma.base_xaccl / 8.0
                #friction = 1
                #xaccl = 0
                print("push start")
            else:
                friction = 1
                xaccl = ma.xaccl
            xvel = ma.xvel

        ma.initPushing(direction, friction, xaccl, xvel)
        mb.initPushing(direction, friction, xaccl, xvel)

        return True

    @classmethod
    def check_sides(cls, result: OverlapResult):

        if result.result == Result.CONTACT:
            if result.facing == Facing.RIGHT:
                pass
                rollbackXLeft(result.mva, result.mvb.hb)
                print("ROLLBACK LEFT 198", str(result.mva), str(result.mvb))
            if result.facing == Facing.LEFT:
                pass
                rollbackXRight(result.mva, result.mvb.hb)
                print("ROLLBACK RIGHT 200", str(result.mva), str(result.mvb))
        elif result.result == Result.OVERLAP:
            if result.side == Facing.RIGHT:
                rollbackXLeft(result.mva, result.mvb.hb)
                print("ROLLBACK LEFT 205", str(result.mva), str(result.mvb))
            elif result.side == Facing.LEFT:
                rollbackXRight(result.mva, result.mvb.hb)
                print("ROLLBACK RIGHT 207", str(result.mva), str(result.mvb))
            else:
                if result.vert == Vertical.DOWN:
                    return

                if result.mva.xloc > result.mvb.xloc:
                    rollbackXRight(result.mva, result.mvb.hb)
                    print("ROLLBACK LEFT 218", str(result.mva), str(result.mvb))
                else:
                    rollbackXLeft(result.mva, result.mvb.hb)
                    print("ROLLBACK RIGHT 218", str(result.mva), str(result.mvb))

    @classmethod
    def findInteraction(self, ma : Mover, mb : Mover,
                        result : OverlapResult) -> bool:

        floor_found = False
        if result.result == Result.CONTACT \
            and result.standing == Vertical.DOWN \
            or result.result == Result.OVERLAP \
            and result.vert == Vertical.DOWN:

            if Id.GATE.value == mb.id:
                if ma.yvel > 0.0:
                    gate: Gate = mb
                    gate.modify_interaction()
                    return False

            if ma.yloc < mb.yloc and mb.id != Id.RAMP.value:
                rollbackYUp(ma, mb.hb)

            floor_found = True
            if mb.id == Id.RAMP.value:
                floor_found = False

        do_check_sides = False
        if result.result == Result.CONTACT \
            and result.facing != 0 \
            or result.result == Result.OVERLAP \
            and result.side != 0:
            pass
            do_check_sides = InteractionListener\
                .initInteraction(ma, mb, result)

        if do_check_sides:
            self.check_sides(result)

        return floor_found

    @classmethod
    def blockToBlocks(self, ma : Block, blocks : []) -> tuple[bool, OverlapResult]:
        floor_found = False
        result = OverlapResult()

        for mb in blocks:

            if ma == mb:
                continue

            result: OverlapResult = moverToMover(ma, mb)

            if result.result == Result.CONTACT \
                    and result.facing != 0 \
                    or result.result == Result.OVERLAP \
                    and result.side != 0:

                self.check_sides(result)
                # mb.xvel = ma.xvel
                # mb.xaccl = ma.xaccl
                # mb.max_xvel = ma.max_xvel
                ma.xvel = 0
                ma.xaccl = 0

                if mb.id == Id.BLOCKCHAIN.value:
                    blockchain : BlockChain = mb
                    blockchain.blocks.append(ma)
                    ma.move_state = Move.CHAIN
                    return floor_found, result

                for blockchain in BlockChain.blockchains:
                    if ma in blockchain.blocks:
                        if mb not in blockchain.blocks:
                            blockchain.blocks.append(mb)
                            mb.move_state = Move.CHAIN
                        break
                    elif mb in blockchain.blocks:
                        if ma not in blockchain.blocks:
                            blockchain.blocks.append(ma)
                            ma.move_state = Move.CHAIN
                        break
                else: # loop completes without break
                    BlockChain.blockchains.append(BlockChain())
                    blockchain = BlockChain.blockchains[len(BlockChain.blockchains)-1]
                    blockchain.blocks.append(ma)
                    blockchain.blocks.append(mb)
                    ma.move_state = Move.CHAIN
                    mb.move_state = Move.CHAIN

        return floor_found, result


    @classmethod
    def moverToMovers(self, ma : Mover,
                      movers : [Mover],
                      spawn_events : [SpawnBlock] = []) -> tuple[bool, OverlapResult]:

        floor_found = False
        result = OverlapResult()
        for mb in movers:

            uuida = ma.auuid
            uuidb = mb.auuid

            if (uuida == uuidb):
                continue

            if Id.GATE.value == mb.id:
                gate : Gate = mb
                if not gate.fallthrough_trap_door:
                    continue

            if Id.BLOCK.value == mb.id:
                if mb.move_state in (Move.GOAL, Move.CHAIN):
                    continue

            if (uuida, uuidb) in InteractionListener.listeners.keys():
                listener = InteractionListener.listeners[(uuida, uuidb)]
                #print("check sides in listener", ma, mb.id)
                #self.check_sides(listener.result)
                continue

            if mb.xvel > ma.xvel:
                result: OverlapResult = moverToMover(mb, ma)
            else:
                result : OverlapResult = moverToMover(ma, mb)

            for spawn_event in spawn_events:
                if result.result in (Result.OVERLAP, Result.CONTACT):
                    if spawn_event.mover.auuid == mb.auuid:
                        mb.spawn_switch = True
                        spawn_event.run_event()
                        return floor_found, result

            floor_found = InteractionListener\
                              .findInteraction(ma, mb, result) or floor_found

        return floor_found, result

