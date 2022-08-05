var TILE_SIZE = 75;

var ANIMATION_DURATION_NORMAL = 500;
var ANIMATION_DURATION_SHORT = 100;
var ANIMATION_DURATION_VERYSHORT = 10;

var ANIMATION_DURATION = 500;

ProjectZerg.Game = function (game) {

    this.bot = {
        level_ui: null,
        sprite: null,
        last_heading: 0,
        relZeroX: 0,
        relZeroY: 0,
        tileSize: 0,
        x: 0,
        y: 0,
        angle: 0,
        walkTo: function(x, y) {
            this.x = x;
            this.y = y;
            var tween = this.sprite.game.add.tween(this.sprite);
            this.sprite.animations.play('walk', this.sprite.animations.getAnimation('walk').frameTotal*1000/ANIMATION_DURATION, true);
            var self = this;
            tween.onComplete.add(function() {
                self.sprite.animations.stop(null,true);
                self.sprite.game.tweens.remove(tween);
                self.sprite.x = self.relZeroX + ((self.x + 0.5) * self.tileSize);
                self.sprite.y = self.relZeroY + ((self.y + 0.5) * self.tileSize);
            });
            tween.to({
                    x: this.relZeroX + ((this.x + 0.5) * this.tileSize),
                    y: this.relZeroY + ((this.y + 0.5) * this.tileSize)
                }, ANIMATION_DURATION, Phaser.Easing.Linear.None, true);
        },
        normalizeRotation: function(angle) {
            var normAngle = angle % 360;
            return normAngle > 180 ? (normAngle % 180) - 180 : normAngle;
        },
        rotateLeft: function() {
            this.angle = this.normalizeRotation(this.angle - 90);
            var tween = this.sprite.game.add.tween(this.sprite);
            var self = this;
            tween.onComplete.add(function() {
                self.sprite.game.tweens.remove(tween);
                self.sprite.angle = self.angle;
            });
            tween.to({ angle: this.angle }, ANIMATION_DURATION,
                Phaser.Easing.Linear.None, true);
        },
        rotateRight: function() {
            this.angle = this.normalizeRotation(this.angle + 90);
            var tween = this.sprite.game.add.tween(this.sprite);
            var self = this;
            tween.onComplete.add(function() {
                self.sprite.game.tweens.remove(tween);
                self.sprite.angle = self.angle;
            });
            tween.to({ angle: this.angle }, ANIMATION_DURATION,
                Phaser.Easing.Linear.None, true);
        },
        moveTo: function(x, y, heading) {
            this.x = x;
            this.y = y;
            this.sprite.x = this.relZeroX + (this.x * this.tileSize) + this.sprite.width * 0.5;
            this.sprite.y = this.relZeroY + (this.y * this.tileSize) + this.sprite.height * 0.5;
            this.angle = this.normalizeRotation(heading * 90);
            this.sprite.angle = this.angle;
        }
    };

};

ProjectZerg.Game.prototype = {

    redraw_level: function() {
        for(var i = 0; i < this.game.level.map.length; i++) {
            for(var j = 0; j < this.game.level.map[i].length; j++) {
                var spriteName = "";

                switch(this.game.level.map[i][j]) {
                    case "F":
                        spriteName = "tile_floor";
                        break;
                    case "M":
                        spriteName = this.game.level.logic_map[i][j] ? "tile_memon" : "tile_memoff";
                        break;
                    case "W":
                        spriteName = "tile_wall";
                        break;
                    case "J":
                        spriteName = this.game.level.logic_map[i][j] ? "tile_torch_on" : "tile_torch_off";
                        break;
                    case "E":
                        spriteName = "tile_exit";
                        break;
                    default:
                        continue;
                }

                this.level_ui.map[i][j].animations.stop();
                this.level_ui.map[i][j].animations.destroy();
                this.level_ui.map[i][j].loadTexture(spriteName);
                this.level_ui.map[i][j].animations.add('animate');
                this.level_ui.map[i][j].animations.play('animate', 24, true);
            }
        }
    },

    create: function () {
        this.bot.x = this.game.level.startX;
        this.bot.y = this.game.level.startY;
        this.resize(0, 0);
        this.game.setZergCallbacks(this, this.bot);
    },

    update: function () {

    },

    resize: function (width, height) {

        var level_size_y = this.game.level.map.length * TILE_SIZE;
        var level_size_x = this.game.level.map[0].length * TILE_SIZE;

        var tile_size_x = TILE_SIZE;
        var tile_size_y = TILE_SIZE;

        if (level_size_y > this.game.height) {
            tile_size_y = (this.game.height / level_size_y) * TILE_SIZE;
        }

        if (level_size_x > this.game.width) {
            tile_size_x = (this.game.width / level_size_x) * TILE_SIZE;
        }

        var tile_size = Math.min(tile_size_x, tile_size_y);

        var level_x = ((this.game.width - this.game.level.map[0].length * tile_size) / 2);
        var level_y = ((this.game.height - this.game.level.map.length * tile_size) / 2);

        if (this.level_ui && this.level_ui.map) {
            for (var i = 0; i < this.level_ui.map.length; i++) {
                for (var j = 0; j < this.level_ui.map[0].length; j++) {
                    this.level_ui.map[i][j].destroy();
                }
            }
        }

        this.level_ui = {};
        this.level_ui.map = new Array(this.game.level.map.length);

        for(var i = 0; i < this.game.level.map.length; i++) {
            this.level_ui.map[i] = new Array(this.game.level.map[i].length);

            for(var j = 0; j < this.level_ui.map[i].length; j++) {
                var spriteName = "";

                switch(this.game.level.map[i][j]) {
                    case "F":
                        spriteName = "tile_floor";
                        break;
                    case "M":
                        spriteName = this.game.level.logic_map[i][j] ? "tile_memon" : "tile_memoff";
                        break;
                    case "W":
                        spriteName = "tile_wall";
                        break;
                    case "J":
                        spriteName = this.game.level.logic_map[i][j] ? "tile_torch_on" : "tile_torch_off";
                        break;
                    case "E":
                        spriteName = "tile_exit";
                        break;
                    default:
                        continue;
                }

                this.level_ui.map[i][j] = this.game.add.sprite(level_x + (j * tile_size),
                                                               level_y + (i * tile_size),
                                                               spriteName);
                this.level_ui.map[i][j].width = tile_size;
                this.level_ui.map[i][j].height = tile_size;
                this.level_ui.map[i][j].animations.add('animate');
                this.level_ui.map[i][j].animations.play('animate', 24, true);
            }
        }

        this.bot.level_ui = this.level_ui;

        if (this.bot.sprite) {
            this.bot.sprite.destroy();
        }

        this.bot.sprite = this.game.add.sprite(level_x + (this.bot.x * tile_size),
                                               level_y + (this.bot.y * tile_size), "zerg");
        this.bot.relZeroX = level_x;
        this.bot.relZeroY = level_y;
        this.bot.sprite.width = tile_size;
        this.bot.sprite.height = tile_size;
        this.bot.tileSize = tile_size;
        this.bot.sprite.anchor.setTo(0.5, 0.5);
        this.bot.sprite.x += this.bot.sprite.width * 0.5;
        this.bot.sprite.y += this.bot.sprite.height * 0.5;
        this.bot.sprite.angle = (this.game.level.startFacing * 90);

        this.bot.sprite.animations.add('walk');

    }

};
