ProjectZerg.Preloader = function (game) {

};

ProjectZerg.Preloader.prototype = {

    preload: function () {

        var style = { font: "65px Arial", fill: "#ffffff", align: "center" };

        var text = this.game.add.text(this.game.world.centerX, this.game.world.centerY, "Loading...", style);

        text.anchor.set(0.5);

        this.load.image('tile_floor', STATIC_URL_PREFIX + 'assets/graphics/tiles/floor.png');
        this.load.image('tile_memoff', STATIC_URL_PREFIX + 'assets/graphics/tiles/light_off.png');
        this.load.image('tile_memon', STATIC_URL_PREFIX + 'assets/graphics/tiles/light_on.png');
        this.load.image('tile_wall', STATIC_URL_PREFIX + 'assets/graphics/tiles/wall.png');
        this.load.image('tile_torch_off', STATIC_URL_PREFIX + 'assets/graphics/tiles/torch_unlit.png');
        this.load.image('tile_exit', STATIC_URL_PREFIX + 'assets/graphics/tiles/exit.png');
        this.load.spritesheet('tile_torch_on', STATIC_URL_PREFIX + 'assets/graphics/tiles/torch.png', 100, 100, 4);
        this.load.spritesheet('zerg', STATIC_URL_PREFIX + 'assets/graphics/zerg.png', 100, 100, 7);

    },

    create: function () {

        this.state.start('Game');

    }

};
