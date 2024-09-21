import * as THREE from "three";

export class Animator {
    startTime = new Date();
    endTime = new Date();
  
    constructor() {
      this.updateStartTimestamp();
    }
  
    updateStartTimestamp() {
      this.startTime = new Date();
    }
  
    getEndTime() {
      var timeDiff = this.endTime - this.startTime; //in ms
      var ms = Math.round(timeDiff);
      return ms;
    }
  
    updateEndTimestamp() {
      this.endTime = new Date();
      return this.getEndTime();
    }
  
    update(stlViewer) {
      this.updateEndTimestamp();
      return false;
    }

    finalize(stlViewer) {
        this.duration = this.endTime();
        this.update(stlViewer);
    }
  }
  
  export class CocoonAnimator extends Animator {
    update(stlViewer) {
      super.update();
  
      const t = this.getEndTime() / 500;
  
      var rearRim = stlViewer.findInObjects((obj) => {
        return obj.name === "EDAG_Light_Cocoon_REAR_RIM";
      });
  
      var frontRim = stlViewer.findInObjects((obj) => {
        return obj.name === "EDAG_Light_Cocoon_FRONT_RIM";
      });
  
      var gridHelper = stlViewer.scene.getObjectByName("GridHelper", true);
  
      if (rearRim && frontRim && gridHelper) {
        rearRim.translateX(2469.987);
        rearRim.rotation.x = 0;
        rearRim.rotation.y = 3.14 * Math.sin(t / 4);
        rearRim.rotation.z = 0;
        rearRim.translateX(-2469.987);
  
        frontRim.rotation.x = 0;
        frontRim.rotation.y = 3.14 * Math.sin(t / 4);
        frontRim.rotation.z = 0;
  
        gridHelper.translateX(-Math.cos(t / 4) * 3.14 * 2.27815792);
      }
  
      return false;
    }
  }
  
  export class CameraMoveAnimator extends Animator {
    initialCameraPosition = new THREE.Vector3();
    targetCameraPosition = new THREE.Vector3();
    initialCameraLookAt = new THREE.Vector3();
    objectCenter = new THREE.Vector3();
    initialCameraToFarEdge = 0;
    targetCameraToFarEdge = 0;
    initialGridSize = 0;
    targetGridSize = 0;
    gridPosition = new THREE.Vector3();
    duration = 100;
  
    constructor(
      initialCameraPosition,
      initialCameraToFarEdge,
      targetCameraPosition,
      targetCameraToFarEdge,
      initialGridSize,
      targetGridSize,
      gridPosition,
      initialCameraLookAt,
      objectCenter,
      duration
    ) {
      super();
      this.initialCameraPosition = initialCameraPosition;
      this.initialCameraToFarEdge = initialCameraToFarEdge;
      this.targetCameraPosition = targetCameraPosition;
      this.targetCameraToFarEdge = targetCameraToFarEdge;
      this.initialGridSize = initialGridSize;
      this.targetGridSize = targetGridSize;
      this.gridPosition = gridPosition;
      this.objectCenter = objectCenter;
      this.initialCameraLookAt = initialCameraLookAt;
      this.duration = duration;
    }
  
    easeInOutSine(elapsed, initialValue, finalValue) {
      const amountOfChange = finalValue - initialValue;
      const portion = elapsed / this.duration;
      return (
        (-amountOfChange / 2) * (Math.cos(Math.PI * portion) - 1) + initialValue
      );
    }
  
    easeInOutSine3(elapsed, initialValue, finalValue) {
      const x = this.easeInOutSine(elapsed, initialValue.x, finalValue.x);
      const y = this.easeInOutSine(elapsed, initialValue.y, finalValue.y);
      const z = this.easeInOutSine(elapsed, initialValue.z, finalValue.z);
      return new THREE.Vector3(x, y, z);
    }
  
    update(stlViewer) {
      super.update();
      if (stlViewer.objects.children.length > 0) {
        var gridZ = new THREE.Box3().setFromObject(stlViewer.objects).min.z;
      } else {
        var gridZ = 0;
      }
      const t = Math.min(this.getEndTime(), this.duration);
      const cameraPosition = this.easeInOutSine3(
        t,
        this.initialCameraPosition,
        this.targetCameraPosition
      );
      const gridPosition = this.easeInOutSine3(
        t,
        this.gridPosition,
        new THREE.Vector3(0, 0, gridZ)
      );
      const far = this.easeInOutSine(
        t,
        this.initialCameraToFarEdge,
        this.targetCameraToFarEdge
      );
      const gridSize = this.easeInOutSine(
        t,
        this.initialGridSize,
        this.targetGridSize
      );
      const lookAtVector = this.easeInOutSine3(
        t,
        this.initialCameraLookAt,
        this.objectCenter
      );
  
      stlViewer.setCameraPosition(cameraPosition, lookAtVector, far);
      stlViewer.loadGrid(gridSize);
      stlViewer.scene
        .getObjectByName("GridHelper", true)
        .position.set(gridPosition.x, gridPosition.y, gridPosition.z);
  
      return t >= this.duration;
    }
  }