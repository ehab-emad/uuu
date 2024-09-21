import * as THREE from './three.js/build/three.module.min.js';
import * as HIDING from "./ModelViewerInternals/ModelViewerObjectsHiding.js";
import * as ANIMATORS from "./ModelViewerInternals/ModelViewerAnimators.js";
import { EffectComposer } from "./three.js/examples/jsm/postprocessing/EffectComposer.js";
import { STLLoader } from "./three.js/examples/jsm/loaders/STLLoader.js";
import { GLTFLoader } from "./three.js/examples/jsm/loaders/GLTFLoader.js";
import { GLTFExporter } from "./three.js/examples/jsm/exporters/GLTFExporter.js";
import { OrbitControls } from "./three.js/examples/jsm/controls/OrbitControls.js";
import { TransformControls } from "./three.js/examples/jsm/controls/TransformControls.js";
import { Sky } from "./three.js/examples/jsm/objects/Sky.js";
import { RenderPass } from ".//three.js/examples/jsm/postprocessing/RenderPass.js";
import { OutlinePass } from "./three.js/examples/jsm/postprocessing/OutlinePass.js";
import { OutputPass } from "./three.js/examples/jsm/postprocessing/OutputPass.js";

export class StlViewer {
  objects = new THREE.Group();
  editingGroup = new THREE.Group();
  scene = new THREE.Scene();
  clock = new THREE.Clock();
  rayCaster = new THREE.Raycaster();
  camera = new THREE.PerspectiveCamera(75, 1, 0.6, 100000);
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  clickedPos = new THREE.Vector2();
  pivotPointPosition = new THREE.Vector3(0, 0, 0);
  selectedObjects = [];
  highlightedObjects = [];
  cameraControls = null;
  transformControls = null;
  composer = null;
  canvasDiv = "";
  animator = [];
  scriptFolder = "";
  onSelection = null;
  gridSize = 0;
  selectInvisible = true;
  localClippingPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
  localClippingPlaneHelper = null;

  constructor(canvasDivName, animator, scriptFolder, onSelection = null) {  
    document.addEventListener("DOMContentLoaded", () => {
      this.init(canvasDivName, animator, scriptFolder, onSelection);
    });
  }

  update() {
    if (this.localClippingPlaneHelper != null) {
      var normal = new THREE.Vector3();
      var point = new THREE.Vector3();
      normal
        .set(0, 0, 1)
        .applyQuaternion(this.localClippingPlaneHelper.quaternion);
      point.copy(this.localClippingPlaneHelper.position);
      this.localClippingPlane.setFromNormalAndCoplanarPoint(normal, point);
    }
    if (this.animator.length > 0) {
      const done = this.animator[this.animator.length - 1].update(this);
      if (done) {
        this.animator.pop();
      }
    }
  }

  #removeFromScene(id) {
    var sceneObject = this.scene.getObjectById(id);
    if (sceneObject !== null) {
      this.scene.remove(sceneObject);
    }
  }

  removeObjects(objects = this.objects) {
    console.log("Objects removed");
    let objectsCopy = [...objects.children];
    for (let obj of objectsCopy) {
      this.removeObjects(obj);
    }
    objects.children = [];
    if (objects === this.objects) {
      this.#emptySelection();
      this.#initializePivotPoint();
    }
  }

  findInObjects(predicate, object = this.objects) {
    if (predicate(object)) return object;
    for (let child of object.children) {
      let found = this.findInObjects(predicate, child);
      if (found != null) {
        return found;
      }
    }
    return null;
  }

  loadObjectsFromDataSrc() {
    var dataSrc = this.canvasDiv.getAttribute("data-src");
    var stlFileDict = null;
    try {
      stlFileDict = JSON.parse(dataSrc);
    } catch (e) {
      stlFileDict = null;
    }
    if (stlFileDict !== null) {
      this.loadSTLs(stlFileDict, true);
    } else {
      if (dataSrc.endsWith("stl")) {
        this.loadSTL(dataSrc, true);
      } else {
        this.loadGLTF(dataSrc, true);
      }
    }
  }

  #onResize() {
    var canvasPosition = this.canvasDiv.getBoundingClientRect();
    var width = canvasPosition.width;
    var height = width;
    this.renderer.setSize(width, height);
    this.composer.setSize(width, height);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  #enableTransformControls() {
    this.transformControls.enabled = true;
    this.#updatePivotPointVisibility();
    if (this.isClippingPlaneEnabled()) {
      this.setPivotPoint(this.#getObjectCenter(this.localClippingPlaneHelper));
    } else {
      this.#updateEditingGroup();
      this.setPivotPoint(this.#getObjectCenter(this.editingGroup));
    }
  }

  #disableTransformControls() {
    this.transformControls.enabled = false;
    this.#updatePivotPointVisibility();
    this.#updateTransfromControlAttachment();
  }

  toggleVisibleOnlySelection() {
    this.selectInvisible = !this.selectInvisible;
  }

  #onKeyUp(event) {
    switch (event.keyCode) {
      case 82: // (R)otate
        if (
          this.transformControls.getMode() == "rotate" &&
          this.transformControls.enabled == true
        ) {
          this.#disableTransformControls();
        } else {
          this.transformControls.setMode("rotate");
          this.#enableTransformControls();
        }
        break;
      case 84: // (T)ranslate
        if (
          this.transformControls.getMode() == "translate" &&
          this.transformControls.enabled == true
        ) {
          this.#disableTransformControls();
        } else {
          this.transformControls.setMode("translate");
          this.#enableTransformControls();
        }
        break;
      case 72: // (H)ide
        HIDING.toggleObjectsHiding(this.selectedObjects);
        HIDING.break;
      case 86: // (V)isible selection only
        this.toggleVisibleOnlySelection();
        break;
      case 67: // (C)lipping plane
        this.toggleClippingPlane();
        break;
    }
  }

  refreshClippingPlaneHelper() {
    var boundingBox = new THREE.Box3();
    var sphere = new THREE.Sphere();
    boundingBox.setFromObject(this.objects);
    boundingBox.getBoundingSphere(sphere);
    if (this.localClippingPlaneHelper == null) {
      this.localClippingPlaneHelper = new THREE.Mesh(
        new THREE.PlaneGeometry(sphere.radius / 10, sphere.radius / 10),
        new THREE.MeshStandardMaterial({
          color: 0x88ff88,
          side: THREE.DoubleSide,
        })
      );
      this.localClippingPlaneHelper.name = "ClippingPlaneHelper";
      this.localClippingPlaneHelper.visible = this.isClippingPlaneEnabled();
    }
    if (
      this.findInObjects((obj) => obj === this.localClippingPlaneHelper) == null
    ) {
      this.addToObjects(this.localClippingPlaneHelper);
    }
  }

  isClippingPlaneEnabled() {
    return this.renderer.localClippingEnabled;
  }

  enableClippingPlane() {
    this.#emptySelection();
    for (let obj of this.objects.children) {
      if (obj.material != undefined && obj.name != "ClippingPlaneHelper") {
        obj.material.clippingPlanes = [this.localClippingPlane];
        obj.material.alphaToCoverage = true;
      }
    }
    this.refreshClippingPlaneHelper();
    this.renderer.localClippingEnabled = true;
    this.localClippingPlaneHelper.visible = true;
    this.#updateTransfromControlAttachment();
  }

  disableClippingPlane() {
    this.renderer.localClippingEnabled = false;
    this.localClippingPlaneHelper.visible = false;
    this.#updateTransfromControlAttachment();
  }

  toggleClippingPlane() {
    if (this.isClippingPlaneEnabled()) {
      this.disableClippingPlane();
    } else {
      this.enableClippingPlane();
    }
  }

  #updateEditingGroup() {
    if (this.findInObjects((obj) => obj === this.editingGroup) == null) {
      this.editingGroup.name = "Editing group";
      this.objects.add(this.editingGroup);
    }
    let editingGroupObjects = [...this.editingGroup.children];
    for (let obj of editingGroupObjects) {
      this.objects.attach(obj);
    }

    this.editingGroup.position.copy(this.pivotPointPosition);
    for (let obj of this.selectedObjects) {
      this.editingGroup.attach(obj);
    }
  }

  #updateTransfromControlAttachment() {
    if (this.transformControls.enabled) {
      if (this.isClippingPlaneEnabled()) {
        this.transformControls.attach(this.localClippingPlaneHelper);
      } else if (this.selectedObjects.length > 0) {
        this.#updateEditingGroup();
        this.transformControls.attach(this.editingGroup);
      } else {
        this.transformControls.detach();
      }
    } else {
      this.transformControls.detach();
    }
  }

  #evaluateMousePosition(event) {
    var canvasPosition = this.canvasDiv.getBoundingClientRect();
    var mousePosition = new THREE.Vector2();
    mousePosition.x =
      ((event.clientX - canvasPosition.left) / canvasPosition.width) * 2 - 1;
    mousePosition.y =
      -((event.clientY - canvasPosition.top) / canvasPosition.height) * 2 + 1;
    this.rayCaster.setFromCamera(mousePosition, this.camera);
    const allIntersections = this.rayCaster.intersectObjects(
      this.objects.children,
      true
    );
    var intersection = false;
    for (let i = 0; i < allIntersections.length; i++) {
      // Filter out invisible if needed
      if (
        !this.selectInvisible &&
        HIDING.isObjectHidden(allIntersections[i].object)
      )
        continue;
      // Filter out points that are on invisible side of clipping plane
      if (
        this.isClippingPlaneEnabled() &&
        allIntersections[i].object.material.clippingPlanes != null &&
        allIntersections[i].object.material.clippingPlanes.length > 0 &&
        this.localClippingPlane.distanceToPoint(allIntersections[i].point) <= 0
      )
        continue;
      // Filter out clipping plane helper
      if (allIntersections[i].object.name == "ClippingPlaneHelper") continue;
      intersection = allIntersections[i];
      break;
    }
    return [mousePosition, intersection];
  }

  #onMouseDown(event) {
    debugger;
    event.preventDefault();
    // for(animator of this.animator)
    // {
    //   animator.finalize();
    // }
    this.animator.length = 0;
    var intersects;
    [this.clickedPos, intersects] = this.#evaluateMousePosition(event);
    if (intersects == false && !event.ctrlKey) {
      this.highlightedObjects.length = 0;
    }
  }

  #updatePivotPointVisibility() {
    var pivot_point_object = this.findInObjects(
      (obj) => obj.name == "Pivot_point"
    );
    if (pivot_point_object != null) {
      pivot_point_object.visible =
        this.transformControls.enabled && !this.isClippingPlaneEnabled();
    }
  }

  setPivotPoint(point) {
    var pivot_point_object = this.findInObjects(
      (obj) => obj.name == "Pivot_point"
    );
    this.pivotPointPosition = point;
    if (pivot_point_object == null) {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute([point.x, point.y, point.z], 3)
      );
      const sprite = new THREE.TextureLoader().load(
        this.scriptFolder + "/sprites/disc.png"
      );
      sprite.colorSpace = THREE.SRGBColorSpace;
      const material = new THREE.PointsMaterial({
        size: 7,
        sizeAttenuation: false,
        map: sprite,
        alphaTest: 0.5,
        transparent: true,
      });
      material.color.setHSL(0.4, 1.0, 0.55, THREE.SRGBColorSpace);
      pivot_point_object = new THREE.Points(geometry, material);
      pivot_point_object.name = "Pivot_point";
      this.addToObjects(pivot_point_object);
      this.#updatePivotPointVisibility();
    } else {
      if (!this.transformControls.enabled) return;
      pivot_point_object.geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute([point.x, point.y, point.z], 3)
      );
    }
    this.#updateTransfromControlAttachment();
  }

  addPoints(vertices = [0, 0, 0]) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(vertices, 3)
    );
    const sprite = new THREE.TextureLoader().load(
      this.scriptFolder + "/sprites/disc.png"
    );
    sprite.colorSpace = THREE.SRGBColorSpace;
    const material = new THREE.PointsMaterial({
      size: 5,
      sizeAttenuation: false,
      map: sprite,
      alphaTest: 0.5,
      transparent: true,
    });
    material.color.setHSL(1.0, 0.3, 0.7, THREE.SRGBColorSpace);
    const particles = new THREE.Points(geometry, material);
    this.addToObjects(particles);
  }

  addLines(
    lines = [
      [
        [0, 0, 0],
        [100, 100, 100],
      ],
    ]
  ) {
    for (var line of lines) {
      this.addLine(line[0], line[1]);
    }
  }

  addLine(start_point, end_point) {
    const vertices = [];
    vertices.push(...start_point);
    vertices.push(...end_point);
    this.addWire(vertices);
  }

  addWire(vertices = [0, 0, 0, 1000, 1000, 1000, 2000, 0, 0]) {
    const geometry = new THREE.BufferGeometry();
    const material = new THREE.LineBasicMaterial({ vertexColors: true });
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(vertices, 3)
    );
    var line = new THREE.Line(geometry, material);
    this.addToObjects(line);
  }

  #emptySelection() {
    this.selectedObjects.length = 0;
    this.#updateEditingGroup();
    this.transformControls.detach();
  }

  #handleSelection(event) {
    if (this.isClippingPlaneEnabled()) return;
    const [mousePosition, intersects] = this.#evaluateMousePosition(event);

    if (
      Math.abs(this.clickedPos.x - mousePosition.x) > 0.05 ||
      Math.abs(this.clickedPos.y - mousePosition.y) > 0.05
    ) {
      return;
    }

    if (!event.ctrlKey) {
      this.#emptySelection();
    }

    if (intersects != false) {
      let indexSelected = this.selectedObjects.indexOf(intersects.object);
      if (indexSelected == -1) {
        this.selectedObjects.push(intersects.object);
        this.#updateEditingGroup();
        this.setPivotPoint(this.#getObjectCenter(this.editingGroup));
      } else {
        this.selectedObjects.splice(indexSelected, 1);
        this.#updateEditingGroup();
      }
      if (this.transformControls.enabled) {
        this.#updateTransfromControlAttachment();
      }

      const objectName = intersects.object.name;
      if (this.onSelection !== null && !event.ctrlKey) {
        this.onSelection(objectName);
      }
    }
  }

  #handlePivotSelection(event) {
    var x_plane = new THREE.Mesh(
      new THREE.PlaneGeometry(100000, 100000, 2, 2),
      new THREE.MeshBasicMaterial({
        visible: false,
        wireframe: true,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.1,
        toneMapped: false,
      })
    );
    x_plane.name = "X_Plane";
    this.addToObjects(x_plane);
    const [mousePosition, intersects] = this.#evaluateMousePosition(event);
    this.removeFromObjects(x_plane);

    if (
      Math.abs(this.clickedPos.x - mousePosition.x) > 0.05 ||
      Math.abs(this.clickedPos.y - mousePosition.y) > 0.05
    ) {
      return;
    }
    if (intersects != false) {
      this.setPivotPoint(intersects.point);
    }
  }

  #onMouseUp(event) {
    event.preventDefault();
    switch (event.button) {
      case 0: // Left button
        this.#handleSelection(event);
        break;
      case 2: // Right button
        this.#handlePivotSelection(event);
        break;
    }
  }

  #onMouseMove(event) {
    event.preventDefault();
    this.highlightedObjects.length = 0;

    if (this.transformControls.enabled || this.isClippingPlaneEnabled()) {
      return;
    }
    const [, intersects] = this.#evaluateMousePosition(event);

    if (intersects != false) {
      let indexSelected = this.selectedObjects.indexOf(intersects.object);
      if (indexSelected == -1 || this.selectedObjects.length > 1) {
        this.highlightedObjects.push(intersects.object);
      }
    }
  }

  removeFromObjects(object) {
    if (object == null) return;
    const parent = object.parent;
    let objIndex = parent.children.indexOf(object);
    parent.children.splice(objIndex, 1);
  }

  addToObjects(newObjects) {
    if (arguments.length > 1) {
      for (let arg of arguments) {
        this.addToObjects(arg);
      }
    } else {
      this.objects.add(newObjects);
    }
  }

  loadGLTF(path, replace = true, manager = THREE.DefaultLoadingManager) {
    const loader = new GLTFLoader(manager);
    loader.load(
      path,
      // Pass the argument of the onComplete callback to resolve
      (gltf) => {
        if (replace) this.removeObjects();
        this.addToObjects(...gltf.scene.children[0].children);
        if (replace) this.#initializeMoveAnimation();
      },
      // Pass null for onProgress, because ES2015 Promises
      // do not natively report progress.
      null,
      // Pass the argument of the onError callback to reject
      (err) => {
        console.log(err);
      }
    );
  }

  #promiseSTLLoad(path, manager, name, stl_material_dict) {
    return new Promise((resolve, reject) => {
      const loader = new STLLoader(manager);
      loader.load(
        path,
        // Pass the argument of the onComplete callback to resolve
        (stl) => {
          var material_dict = {
            color: stl_material_dict["color"] || new THREE.Color(0xd2d2ff),
            emissive:
              stl_material_dict["emissive"] || new THREE.Color(0x000000),
            roughness: stl_material_dict["roughness"] || 1,
            metalness: stl_material_dict["metalness"] || 0,
            side: THREE.DoubleSide,
          };
          var material = new THREE.MeshStandardMaterial(material_dict);
          var mesh = new THREE.Mesh(stl, material);
          mesh.name = name;
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          resolve(mesh);
        },
        // Pass null for onProgress, because ES2015 Promises
        // do not natively report progress.
        null,
        // Pass the argument of the onError callback to reject
        (err) => {
          reject(err);
        }
      );
    });
  }

  #existsFile(url) {
    var http = new XMLHttpRequest();
    http.open("HEAD", url, false);
    http.send();
    return http.status != 404;
  }

  loadJSON(jsonData, replace = true, manager = THREE.DefaultLoadingManager) {
    if (replace) this.removeObjects();
    let obj_dict = JSON.parse(jsonData);
    for (let key in obj_dict) {
      switch (obj_dict[key]["type"]) {
        case "point":
          this.addPoints(obj_dict[key]["position"]);
          break;
        case "line":
          this.addLine(
            obj_dict[key]["start_point"],
            obj_dict[key]["end_point"]
          );
          break;
        case "wire":
          this.addWire(obj_dict[key]["vertices"]);
          break;
      }
    }
    if (replace) this.#initializeMoveAnimation();
  }

  loadSTL(stlPath, replace = true, manager = THREE.DefaultLoadingManager) {
    if (this.#existsFile(stlPath)) {
      var stlFileDict = {};
      stlFileDict[stlPath] = {};
      this.loadSTLs(stlFileDict, replace, manager);
    } else {
      this.loadObjectsFromDataSrc();
    }
  }

  #initializeMoveAnimation() {
    const [targetCameraPosition, center, cameraToFarEdge, radius] =
      this.#calculateFittedCameraPositions(this.objects, 1.25);
    const gridPosition = this.scene.getObjectByName(
      "GridHelper",
      true
    ).position;
    this.animator.push(
      new ANIMATORS.CameraMoveAnimator(
        structuredClone(this.camera.position),
        this.camera.far / 30,
        targetCameraPosition,
        cameraToFarEdge,
        this.gridSize,
        radius,
        gridPosition,
        this.cameraControls.target,
        center,
        1000
      )
    );
  }

  loadSTLs(
    stlFileDict,
    replace = true,
    manager = THREE.DefaultLoadingManager,
    retries = 10
  ) {
    var promiseArray = [];
    try {
      for (const key in stlFileDict) {
        const url = key;
        if (this.#existsFile(url)) {
          promiseArray.push(
            this.#promiseSTLLoad(url, manager, key, stlFileDict[key]).then()
          );
        }
      }
      if (promiseArray.length > 0) {
        // Notice the spread operator in the push
        Promise.all(promiseArray).then(
          (stls) => {
            if (replace) this.removeObjects();
            this.addToObjects(...stls);
            if (replace) this.#initializeMoveAnimation();
            //var radius = this.#fitCameraToObject(this.objects);
          },
          (error) => {
            console.log(error);
            if (retries > 0) {
              this.loadSTLs(stlFileDict, replace, manager, retries - 1);
            }
          }
        );
      }
    } catch (error) {
      console.log(error);
    }
  }

  #addBBoxToScene(box3) {
    const dimensions = new THREE.Vector3().subVectors(box3.max, box3.min);
    const boxDummyGeo = new THREE.BoxGeometry(
      dimensions.x,
      dimensions.y,
      dimensions.z
    );

    const position = new THREE.Vector3()
      .addVectors(box3.min, box3.max)
      .multiplyScalar(0.5);

    const mesh = new THREE.Mesh(
      boxDummyGeo,
      new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true })
    );
    mesh.position.set(position.x, position.y, position.z);
    this.scene.add(mesh);
    return mesh;
  }

  #getObjectCenter(object) {
    let box3 = new THREE.Box3();
    box3.setFromObject(object);
    const bBoxCenter = new THREE.Vector3()
      .addVectors(box3.min, box3.max)
      .multiplyScalar(0.5);
    if (isNaN(bBoxCenter.x)) return object.position;
    return bBoxCenter;
  }

  #addSphereToScene(sphere) {
    const sphereGeometry = new THREE.SphereGeometry(sphere.radius, 32, 32);

    // move new mesh center so it's aligned with the original object
    const matrix = new THREE.Matrix4().setPosition(sphere.center);
    sphereGeometry.applyMatrix(matrix);
    sphereGeometry.matrixWorldNeedsUpdate = true;

    const mesh = new THREE.Mesh(
      sphereGeometry,
      new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true })
    );
    this.scene.add(mesh);
  }

  #calculateFittedCameraPositions(object, offset) {
    var boundingBox = new THREE.Box3();
    var sphere = new THREE.Sphere();
    boundingBox.setFromObject(object);
    boundingBox.getBoundingSphere(sphere);
    const center = sphere.center;

    const radius = Math.max(sphere.radius * offset, 1);

    const fov = this.camera.fov * (Math.PI / 180);
    const fovh = 2 * Math.atan(Math.tan(fov / 2) * this.camera.aspect);
    const minFov = Math.min(fov, fovh);
    const distanceFromCenter = radius / Math.tan(minFov / 2);
    const axisDistance = (distanceFromCenter * 2) / 3;
    const cameraToFarEdge = distanceFromCenter + radius;
    const targetCameraPosition = new THREE.Vector3(
      center.x - axisDistance,
      center.y - axisDistance,
      center.z + axisDistance / 2
    );

    return [targetCameraPosition, center, cameraToFarEdge, sphere.radius];
  }

  setCameraPosition(targetCameraPosition, center, cameraToFarEdge) {
    // Update camera position
    this.camera.position.z = targetCameraPosition.z;
    this.camera.position.x = targetCameraPosition.x;
    this.camera.position.y = targetCameraPosition.y;
    this.camera.far = cameraToFarEdge * 30;
    this.camera.lookAt(center);
    this.camera.updateProjectionMatrix();

    // Adapt controls
    this.cameraControls.target = center;
    this.cameraControls.maxDistance = cameraToFarEdge * 2;
  }

  #fitCameraToObject(object, offset = 1.25) {
    const [targetCameraPosition, center, cameraToFarEdge, radius] =
      this.#calculateFittedCameraPositions(object, offset);
    this.setCameraPosition(targetCameraPosition, center, cameraToFarEdge);

    return radius;
  }

  #runGameLoop() {
    var delta = this.clock.getDelta();
    requestAnimationFrame(() => this.#runGameLoop());
    this.update();
    this.composer.render(delta);
    this.cameraControls.update(delta);
  }

  #getCanvasId() {
    return "canvas_" + this.canvasDiv.id;
  }

  #initializeCamera() {
    this.camera.position.set(-1000, -2000, 2000);
    this.camera.lookAt(1000, 0, 500);
    this.camera.up.set(0, 0, 1);
  }

  #initializeRenderer() {
    this.renderer.setSize($(this.canvasDiv).width(), $(this.canvasDiv).width());
    this.renderer.autoClear = false;
    this.renderer.setClearColor(0x000000, 0.0);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.5;
    this.renderer.domElement.id = this.#getCanvasId();

    this.canvasDiv.appendChild(this.renderer.domElement);
  }

  #initializeEffects() {
    // Prepare render pass
    var canvasPosition = this.canvasDiv.getBoundingClientRect();
    this.composer = new EffectComposer(this.renderer);
    var renderPass = new RenderPass(this.scene, this.camera);
    this.composer.addPass(renderPass);

    // Prepare outlining for highlighted objects
    var paramsMagenta = {
      edgeStrength: 3.0,
      edgeGlow: 1,
      edgeThickness: 1.0,
      pulsePeriod: 0,
      usePatternTexture: false,
    };
    var outlinePassHighlighted = new OutlinePass(
      new THREE.Vector2(canvasPosition.width, canvasPosition.height),
      this.scene,
      this.camera
    );
    outlinePassHighlighted.renderToScreen = true;
    outlinePassHighlighted.selectedObjects = this.highlightedObjects;
    outlinePassHighlighted.edgeStrength = paramsMagenta.edgeStrength;
    outlinePassHighlighted.edgeGlow = paramsMagenta.edgeGlow;
    outlinePassHighlighted.visibleEdgeColor.set(0xffffff);
    outlinePassHighlighted.hiddenEdgeColor.set(0xff00ff);
    this.composer.addPass(outlinePassHighlighted);

    // Prepare outlining for selected objects
    var paramsOrange = {
      edgeStrength: 3.0,
      edgeGlow: 1,
      edgeThickness: 1.0,
      pulsePeriod: 3,
      usePatternTexture: false,
    };
    var outlinePassSelected = new OutlinePass(
      new THREE.Vector2(canvasPosition.width, canvasPosition.height),
      this.scene,
      this.camera
    );
    outlinePassSelected.renderToScreen = true;
    outlinePassSelected.selectedObjects = this.selectedObjects;
    outlinePassSelected.edgeStrength = paramsOrange.edgeStrength;
    outlinePassSelected.edgeGlow = paramsOrange.edgeGlow;
    outlinePassSelected.visibleEdgeColor.set(0xffbc40);
    outlinePassSelected.hiddenEdgeColor.set(0xffa500);
    this.composer.addPass(outlinePassSelected);

    const outputPass = new OutputPass();
    this.composer.addPass(outputPass);
  }

  #initializeControls() {
    this.cameraControls = new OrbitControls(
      this.camera,
      this.renderer.domElement
    );
    this.cameraControls.maxPolarAngle = Math.PI / 2;
    this.cameraControls.update();

    this.transformControls = new TransformControls(
      this.camera,
      this.renderer.domElement
    );
    this.transformControls.addEventListener("dragging-changed", (event) => {
      this.cameraControls.enabled = !event.value;
    });
    this.transformControls.enabled = false;
    this.scene.add(this.transformControls);
  }

  #initializeLights() {
    // Ambient lights (necessary for Phong/Lambert-materials, not for Basic)
    var ambientLight = new THREE.AmbientLight(0xffffff, 1.3);
    var hemilight = new THREE.HemisphereLight("white", "darkslategrey", 3);
    ambientLight.castShadow = true;
    hemilight.castShadow = true;
    this.scene.add(hemilight);
    this.scene.add(ambientLight);

    // Add fog to "blur" objects in long distance (e.g. grid)
    this.scene.fog = new THREE.Fog(0xa0a0a0, 5000, 20000);

    // Add directional light
    const dirLight = new THREE.DirectionalLight(0xefc070, 5);
    dirLight.position.set(0, 200, 10000);
    dirLight.castShadow = true;
    dirLight.shadow.camera.top = 180;
    dirLight.shadow.camera.bottom = -100;
    dirLight.shadow.camera.left = -120;
    dirLight.shadow.camera.right = 120;
    this.scene.add(dirLight);
  }

  #loadSky() {
    // Create Sun
    var sun = new THREE.Vector3();
    const phi = ((90 - 40) * 3.14) / 180;
    const theta = (70 * 3.14) / 180;
    sun.setFromSphericalCoords(1, phi, theta);

    // Create Sky
    var sky = new Sky();
    sky.scale.setScalar(100000);
    this.scene.add(sky);

    var uniforms = sky.material.uniforms;
    uniforms["turbidity"].value = 20;
    uniforms["rayleigh"].value = 2;
    uniforms["mieCoefficient"].value = 0.005;
    uniforms["mieDirectionalG"].value = 0.9;
    uniforms["up"].value = new THREE.Vector3(0, 0, 1);
    uniforms["sunPosition"].value.copy(sun);
  }

  loadGrid(grid_size) {
    let old_grid = this.scene.getObjectByName("GridHelper");
    if (old_grid != undefined) {
      this.#removeFromScene(old_grid.id);
    }
    this.gridSize = grid_size;
    const grid_lines = 20;
    const grid = new THREE.GridHelper(
      grid_size * grid_lines,
      grid_lines,
      0x000000,
      0x000000
    );
    grid.name = "GridHelper";
    grid.rotation.x = -Math.PI / 2;
    grid.material.opacity = 0.7;
    grid.material.transparent = true;
    this.scene.add(grid);
  }

  #initializeEventListeners() {
    // Resize after viewport-size-change
    window.addEventListener("resize", () => this.#onResize());

    this.canvasDiv.addEventListener("mousedown", (event) =>
      this.#onMouseDown(event)
    );

    this.canvasDiv.addEventListener("mouseup", (event) =>
      this.#onMouseUp(event)
    );
    this.canvasDiv.addEventListener("mousemove", (event) =>
      this.#onMouseMove(event)
    );

    window.addEventListener("keyup", (event) => this.#onKeyUp(event));
  }

  #updateMappingExposure(value) {
    // Increase exposure for lighter object rendering
    this.renderer.toneMappingExposure = value;
  }

  #loadObjects() {
    this.scene.add(this.objects);
  }

  #initializePivotPoint() {
    this.setPivotPoint(new THREE.Vector3(0, 0, 0));
  }

  init(canvasDivName, animator, scriptFolder, onSelection) {
    this.animator.push(animator);
    this.scriptFolder = scriptFolder;
    this.onSelection = onSelection;

    // Store canvas div element
    this.canvasDiv = document.getElementById(canvasDivName);

    // If canvas element already exists, stop initialization not to overwrite existing object
    if (document.getElementById(this.#getCanvasId()) != null) {
      return;
    }

    // Initialize 3D View
    this.#initializeCamera();
    this.#initializeRenderer();
    this.#initializeEffects();
    this.#initializeControls();
    this.#initializeLights();
    this.#initializeEventListeners();

    // Load objects
    this.#loadSky();
    this.loadGrid(10000);
    this.#loadObjects();
    this.loadObjectsFromDataSrc();

    // Initialize Helper objects
    this.#initializePivotPoint();

    // Update exposure to light-up rendered objects
    this.#updateMappingExposure(0.5);

    // Start loop
    this.#runGameLoop();
  }

  exportToJSON() {
    var jsondata = this.scene.toJSON();

    const a = document.createElement("a");
    const file = new Blob([JSON.stringify(jsondata, null, 4)], {
      type: "application/json",
    });
    a.href = URL.createObjectURL(file);
    a.download = "meta_scene_EDAG_Light_Cocoon.json";
    a.click();
  }

  exportToGLTF(binary = true) {
    const exporter = new GLTFExporter();
    const options = {
      trs: false,
      onlyVisible: true,
      binary: binary,
      maxTextureSize: 1024,
    };
    exporter.parse(
      this.objects,
      // called when the gltf has been generated
      function (gltf) {
        if (gltf instanceof ArrayBuffer) {
          var file = new Blob([gltf], {
            type: "application/octet-stream",
          });
        } else {
          const output = JSON.stringify(gltf, null, 2);
          var file = new Blob([output], { type: "text/plain" });
        }
        const a = document.createElement("a");
        a.href = URL.createObjectURL(file);
        if (binary) {
          a.download = "object.glb";
        } else {
          a.download = "object.gltf";
        }
        a.click();
      },
      options
    );
  }
}
