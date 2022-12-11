$(function(){
    window.setInterval(function(){LoadNewData()}, 5000)
    var url_ = window.location.href;
    var parts = url_.split("/");
    var last_part = parts[parts.length - 1];

function LoadNewData(){$.ajax({ url:"/card_watch_main/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_watch_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/card_pause_main/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_pause_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/card_unique_main/"+last_part,
                                type:'POST',
                                success: function(data){$(paragraph_chart_unique_backend).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/dataonline_main/"+last_part,
                                type:'POST',
                                success: function(data){$(chartOnline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/dataoffline_main/"+last_part,
                                type:'POST',
                                success: function(data){$(chartOffline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/dataunique_main/"+last_part,
                                type:'POST',
                                success: function(data){$(chartUniqueOnline).replaceWith(data)}
                            });
                            $.ajax({
                                url:"/tablestat_main/"+last_part,
                                type:'POST',
                                success: function(data){$('#containertable').replaceWith(data)}
                            });
                    };  
});