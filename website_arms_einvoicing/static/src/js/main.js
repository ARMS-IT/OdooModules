odoo.define('website_arms_einvoicing.main', function(require) {
    "use strict";
    $(document).ready(function() {
        var windowOn = $(window);
        windowOn.on('load', function() {
            $("#loading").fadeOut(500);
        });

        $('#countdown').countdown({
            day: 4,
            month: 12,
            year: 2021,
        });
        windowOn.on('scroll', function() {
            var scroll = $(window).scrollTop();
            if (scroll < 100) {
                $("#header-sticky").removeClass("sticky");
            } else {
                $("#header-sticky").addClass("sticky");
            }
        });
        $('.testimonial__slider').owlCarousel({
            loop: true,
            margin: 30,
            autoplay: true,
            autoplayTimeout: 3000,
            smartSpeed: 500,
            items: 6,
            navText: ['<button><i class="fa fa-angle-left"></i>PREV</button>', '<button>NEXT<i class="fa fa-angle-right"></i></button>'],
            nav: false,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 1
                },
                767: {
                    items: 2
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 2
                },
                1600: {
                    items: 2
                }
            }
        });

        $('.testimonial__slider-3').owlCarousel({
            loop: true,
            margin: 30,
            autoplay: true,
            autoplayTimeout: 3000,
            smartSpeed: 500,
            items: 6,
            navText: ['<button><i class="fa fa-angle-left"></i>PREV</button>', '<button>NEXT<i class="fa fa-angle-right"></i></button>'],
            nav: false,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 1
                },
                767: {
                    items: 2
                },
                992: {
                    items: 2
                },
                1200: {
                    items: 3
                },
                1600: {
                    items: 3
                }
            }
        });
        $('.testimonial__slider-5').owlCarousel({
            loop: true,
            margin: 30,
            autoplay: true,
            autoplayTimeout: 3000,
            smartSpeed: 500,
            items: 6,
            navText: ['<button><i class="fa fa-angle-left"></i>PREV</button>', '<button>NEXT<i class="fa fa-angle-right"></i></button>'],
            nav: false,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 1
                },
                767: {
                    items: 1
                },
                992: {
                    items: 1
                },
                1200: {
                    items: 1
                },
                1600: {
                    items: 1
                }
            }
        });
        $('.team__slider ').owlCarousel({
            loop: true,
            margin: 30,
            autoplay: false,
            autoplayTimeout: 3000,
            smartSpeed: 500,
            items: 6,
            navText: ['<button><i class="fa fa-angle-left"></i>PREV</button>', '<button>NEXT<i class="fa fa-angle-right"></i></button>'],
            nav: false,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 1
                },
                767: {
                    items: 2
                },
                992: {
                    items: 3
                },
                1200: {
                    items: 3
                },
                1600: {
                    items: 3
                }
            }
        });

        if ($('.scene').length > 0) {
            $('.scene').parallax({
                scalarX: 10.0,
                scalarY: 15.0,
            });
        };

        $('.hover__active').on('mouseenter', function() {
            $(this).addClass('active').parent().siblings().find('.hover__active').removeClass('active');
        });

    });
});