const slider = document.querySelector('.slider-container'),
    slides = Array.from(document.querySelectorAll('.slide'))

const ratingStars = []
for (let i = 1; i <= slides.length; i++) {
    ratingStars.push([...document.getElementsByClassName("rating__star_"+i)]);
}

let isDragging = false,
    startPos = 0,
    currentTranslate = 0,
    prevTranslate = 0,
    animationID = 0,
    currentIndex = 0,
    vote

slides.forEach((slide, index) => {
    const slideImgInf = slide.querySelector('.img-container')
    slideImgInf.addEventListener('dragstart', (e) => e.preventDefault())

    //Touch events
    slide.addEventListener('touchstart', touchStart(index))
    slide.addEventListener('touchend', touchEnd)
    slide.addEventListener('touchmove', touchMove)

    //Mouse events
    slide.addEventListener('mousedown', touchStart(index))
    slide.addEventListener('mouseup', touchEnd)
    slide.addEventListener('mouseleave', touchEnd)
    slide.addEventListener('mousemove', touchMove)
})

//disable context menu
window.oncontextmenu = function(event) {
    event.preventDefault()
    event.stopPropagation()
    return false
}

function touchStart(index) {
    return function(event) {
        currentIndex = index
        startPos = getPositionX(event)
        isDragging = true

        animationID = requestAnimationFrame(animation)
        slider.classList.add('grabbing')
    }
}

function touchEnd() {
    isDragging = false
    cancelAnimationFrame(animationID)

    const movedBy = currentTranslate - prevTranslate

    if(movedBy < -75 && currentIndex < slides.length -1)
    currentIndex += 1

    if(movedBy > 75 && currentIndex > 0)
    currentIndex -= 1

    setPositionByIndex()

    slider.classList.remove('grabbing')

    executeRating(ratingStars[currentIndex], currentIndex +1);
}

function touchMove(event) {
    if(isDragging) {
        const currentPosition = getPositionX(event)
        currentTranslate = prevTranslate + currentPosition - startPos
    }
}

function getPositionX(event) {
    return event.type.includes('mouse')
    ? event.pageX
    : event.touches[0].clientX
}

function animation() {
    setSliderPosition()
    if(isDragging) requestAnimationFrame(animation)
}

function setSliderPosition() {
    slider.style.transform = `translateX(${currentTranslate}px)`
}

function setPositionByIndex() {
    currentTranslate = currentIndex * -window.innerWidth
    prevTranslate = currentTranslate
    setSliderPosition()
}

////////////////////////////////////////////////////////////////////////////////////////////////

function executeRating(stars, j) {
    const starClassActive = "rating__star_"+j+" fas fa-star fa-3x";
    const starClassInactive = "rating__star_"+j+" far fa-star fa-3x";
    const starsLength = stars.length;
    let i;
    stars.map((star) => {
        star.onclick = () => {
            i = stars.indexOf(star);

            if (star.className===starClassInactive) {        
                for (i; i >= 0; --i) stars[i].className = starClassActive;
            }
            else {
                for (i; i < starsLength; ++i) stars[i].className = starClassInactive;
            }

            vote = 0
            for (let ind = 0; ind < starsLength; ind++) {
            if (stars[ind].className===starClassActive) {
                vote += 1;
                }
            }
            document.getElementById("vote_"+j).value = vote;
        };
    });
}
 