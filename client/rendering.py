from __future__ import division, print_function

import sfml

import engine.gamestate
import constants

import function

import map_renderer
import character_renderer
import weapon_renderer
import projectile_renderer
import sentry_renderer
#import spectator
import engine.character
import engine.weapon
import engine.projectile
import engine.sentry
import hud_renderer

class GameRenderer(object):
    def __init__(self, client):
        self.window = client.window

        self.interpolated_state = engine.gamestate.Gamestate()
        self.renderers = {}
        self.focus_object_id = None

        self.view_width = constants.GAME_WIDTH
        self.view_height = constants.GAME_HEIGHT
    
        mapList = [
            "montane/montane0",
            "montane/montane1",
            "montane/montane2",
            "montane/montane3",
            "montane/montane4",
            "montane/montane5",
            "montane/montane6",
            "montane/montane7",
        ]
        self.maprenderer = map_renderer.MapRenderer(self, mapList)
        self.healthhud = None
        self.overlayblits = []

        self.renderers = {
            engine.character.Scout: character_renderer.ScoutRenderer(),
            engine.character.Pyro: character_renderer.PyroRenderer(),
            engine.character.Soldier: character_renderer.SoldierRenderer(),
            engine.character.Heavy: character_renderer.HeavyRenderer(),
            engine.character.Medic: character_renderer.MedicRenderer(),
            engine.character.Engineer: character_renderer.EngineerRenderer(),
            engine.character.Spy: character_renderer.SpyRenderer(),
            engine.character.Quote: character_renderer.QuoteRenderer(),
            engine.weapon.Scattergun: weapon_renderer.ScattergunRenderer(),
            engine.weapon.Flamethrower: weapon_renderer.FlamethrowerRenderer(),
            engine.weapon.Rocketlauncher: weapon_renderer.RocketlauncherRenderer(),
            engine.weapon.Minigun: weapon_renderer.MinigunRenderer(),
            engine.weapon.Medigun : weapon_renderer.MedigunRenderer(),
            engine.weapon.Shotgun: weapon_renderer.ShotgunRenderer(),
            engine.weapon.Revolver: weapon_renderer.RevolverRenderer(),
            engine.weapon.Blade: weapon_renderer.BladeRenderer(),
            engine.projectile.Shot: projectile_renderer.ShotRenderer(),
            engine.projectile.Flame: projectile_renderer.FlameRenderer(),
            engine.projectile.Rocket: projectile_renderer.RocketRenderer(),
            engine.projectile.Needle: projectile_renderer.NeedleRenderer(),
            engine.projectile.Blade: projectile_renderer.BladeRenderer(),
            engine.sentry.Building_Sentry: sentry_renderer.BuildingSentryRenderer(),
            engine.sentry.Sentry: sentry_renderer.SentryRenderer(),
        }

        self.world_sprites = []
        self.hud_overlay = []
        self.hud_sprites = []

        self.rendering_stack = []

    def render(self, client, game, frametime):    
        # reset spritegroups
        self.world_sprites = []
        self.hud_sprites = []
        self.hud_overlay = []

        self.window = client.window

        # Gather in one (chronological) list all the states we have
        states = game.old_server_states[:]
        if game.current_state.time > states[-1].time:
            # Add current state to the states if there isn't already a server state which is new enough
            states.append(game.current_state.copy())
        if game.current_state.time + constants.PHYSICS_TIMESTEP > states[-1].time:
            # Also make a uber-new state for  the game.accumulator
            newest_state = game.current_state.copy()
            newest_state.update_all_objects(game, constants.PHYSICS_TIMESTEP)
            states.append(newest_state)

        # Target time is the time of the state we would like
        target_time = game.current_state.time + game.accumulator - constants.INTERP_BUFFER_LENGTH
        if target_time < 0:
            # We're not even supposed to be rendering yet
            # Exit
            return

        if states[0].time > target_time or len(states) < 2:
            # We don't have old enough states to be able to interpolate properly
            # Take the oldest one and move it back in time
            self.interpolated_state = states[0].copy()
            self.interpolated_state.update_all_objects(game, target_time - self.interpolated_state.time)
        else:
            # Now we need to find the two states that bracket target_time
            # Easier to do this by looping over index
            for i in range(len(states)-1):
                if states[i].time <= target_time <= states[i+1].time:
                    states = states[i:i+2]
                    break            
            alpha = (target_time - states[0].time)/(states[1].time - states[0].time)
            # Interpolate
            self.interpolated_state.interpolate(states[0], states[1], alpha)

        # Get rid of all of the server states which we don't need anymore
        # We can leave one old server state though to interpolate
        # Remember that the states are chronologically sorted
        index = 0
        while index < len(game.old_server_states)-1:
            if game.old_server_states[index+1].time < target_time:
                game.old_server_states.pop(index)
                index -= 1
            index += 1

        focus_object_id = self.interpolated_state.players[client.our_player_id].character_id

        if focus_object_id != None:
            client.spectator.x = self.interpolated_state.entities[focus_object_id].x
            client.spectator.y = self.interpolated_state.entities[focus_object_id].y

            if self.interpolated_state.entities[focus_object_id].just_spawned:
                self.healthhud = None
                self.healthhud = hud_renderer.HealthRenderer(self, game, self.interpolated_state, focus_object_id)
                self.interpolated_state.entities[focus_object_id].just_spawned = False
            self.healthhud.render(self, game, self.interpolated_state, focus_object_id)

        else:
            if self.healthhud != None:
                self.healthhud = None
            player = self.interpolated_state.players[client.our_player_id]
            if player.left:
                client.spectator.x -= 800*frametime
            elif player.right:
                client.spectator.x += 800*frametime
            if player.up:
                client.spectator.y -= 800*frametime
            elif player.down:
                client.spectator.y += 800*frametime
        # update view
        self.xview = int(round(client.spectator.x - self.view_width / 2))
        self.yview = int(round(client.spectator.y - self.view_height / 2))

        # clear screen if needed
        if client.spectator.x <= self.view_width / 2 or client.spectator.x + self.view_width >= game.map.width or client.spectator.y <= self.view_height / 2 or self.yview + self.view_height >= game.map.height:
            self.window.clear()

        # draw background
        self.maprenderer.render(self, self.interpolated_state)
        # draw entities
        self.rendering_stack = []
        for entity in self.interpolated_state.entities.values():
            self.rendering_stack.append(entity)

        self.rendering_stack.sort(key=lambda entityobject: self.renderers[type(entityobject)].depth) # Reorder by depth attribute
        for entity in self.rendering_stack:
            self.renderers[type(entity)].render(self, game, self.interpolated_state, entity)

        # draw health bars
        for self.overlay in self.hud_overlay: #Call the render of all the objects
            self.overlay.render(self, game, self.interpolated_state)
        # draw hud sprites
        for hud_sprite in self.hud_sprites:
            self.window.draw(hud_sprite)

    def get_screen_coords(self, x, y):
        # calculate drawing position
        draw_x = int(round(x - self.xview))
        draw_y = int(round(y - self.yview))

        return draw_x, draw_y
