// Object hiding/unhiding logic
export function isObjectHidden(object) {
  return !(object.hidden == undefined || object.hidden == false);
}

function hideObject(object) {
  object.hidden = true;
  object.material.transparent = true;
  object.material.opacity = 0;
}

function unhideObject(object) {
  object.hidden = false;
  object.material.opacity = 1;
}

export function toggleObjectsHiding(objects) {
  let makeHidden = objects.some((obj) => !isObjectHidden(obj));

  for (let obj of objects) {
    if (makeHidden) {
      hideObject(obj);
    } else {
      unhideObject(obj);
    }
  }
}
