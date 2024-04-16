$(function(){
    var index=0;//标记当前图片索引
    var f;
    function newsclock(){
        f=setInterval(function(){
            if(index==$(".slides li").length-1){
                index=0;
                $(".slides li").css("opacity","0");
                $(".slides li").eq(index).css("opacity","1");
                $(".dotnumb").css("background-color","#bbb");
                $(".dotnumb").css("width","15px");
                $(".dotnumb").eq(index).css("background-color","#eee");
                $(".dotnumb").eq(index).css("width","25px");
            }else{
                index++;
                $(".slides li").css("opacity","0");
                $(".slides li").eq(index).css("opacity","1");
                $(".dotnumb").css("background-color","#bbb");
                $(".dotnumb").css("width","15px");
                $(".dotnumb").eq(index).css("background-color","#eee");
                $(".dotnumb").eq(index).css("width","25px");
            }
        },4000)
    }
    newsclock();

    $(".dotnumb").click(function(){
        clearInterval(f);
        var indexx=$(this).index();
        index=indexx;
            $(".slides li").css("opacity","0");
            $(".slides li").eq(index).css("opacity","1");
            $(".dotnumb").css("background-color","#bbb");
            $(".dotnumb").css("width","15px");
            $(".dotnumb").eq(index).css("background-color","#eee");
            $(".dotnumb").eq(index).css("width","25px");
        newsclock();
    })
})
