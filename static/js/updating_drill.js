$(function(){
    window.setInterval(function(){LoadNewData()}, 5000)
    var url_ = window.location.href;
    var parts = url_.split("/");
    var last_part = parts[parts.length - 1];
    var l_part= parts[parts.length - 3];

    console.log(url_)
    console.log('l_part',l_part)
    console.log('last_part',last_part)
    
function LoadNewData(){
                            $.ajax({
                                url:"/card_watch_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_watch_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/card_pause_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_pause_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/card_unique_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_unique_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/unique_watch/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_unique_backend2).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/peak_data/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_peak_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/avd_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(card_avd_time).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/avdprct_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(card_prct_time).replaceWith(data)}
                            });

                            $.ajax({
                                url:"/dataonline_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(chartOnline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/dataoffline_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(chartOffline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/dataunique_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){$(chartUniqueOnline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/tablestat_drill/"+l_part+"/"+last_part,
                                type:'POST',
                                success: function(data){var position= $('.creatingspace').scrollTop()
                                                         $('.creatingspace').replaceWith(data)
                                                         $('.creatingspace').scrollTop(position);}
                            });

                    };  
});





