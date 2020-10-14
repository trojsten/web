hideFunction = element => element.style.visibility="hidden"
showFunction = element => element.style.visibility="visible"

makeSpans = (element) => {
    element.textContent.split("").reverse().forEach((char) => {
        let s = document.createElement("span");
        s.innerHTML = char;
        element.parentNode.insertBefore(s, element.parentNode.firstChild);
    })
}
recursivelyMakeSpans = (element, depth) => {
    if(depth>8) return;
    if(element.nodeType===element.TEXT_NODE){
        makeSpans(element);
        element.parentNode.removeChild(element);
        return;
    }
    if(element.childNodes.length!==0){
    return Array.from(element.childNodes).map((childNode) => recursivelyMakeSpans(childNode, depth+1));
    }
}
let time = 0;
recursivelyApplyFunction = (element, fx, timeDelta=0,depth=0) => {
    if (depth > 8) return;
    if(element.childElementCount===0) {
        ((time) => setTimeout(() => fx(element),time))(time);
        time+=timeDelta;
        return;
    }
    ((time) => setTimeout(() => {
        fx(element);
    },time))(time);
    Array.from(element.children).forEach(child => {
        recursivelyApplyFunction(child, fx, timeDelta,depth+1);
    });
}
setTimeout(() =>{
recursivelyMakeSpans(document.querySelector("body"));
recursivelyApplyFunction(document.querySelector("body"),hideFunction);
recursivelyApplyFunction(document.querySelector("body"), showFunction,50);
},1000)
//document.querySelectorAll("span").forEach(span=> span.style.visibility = "visible");

//TODO: pexeso
//TODO: tlačidlá
