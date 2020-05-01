exports.handler = async (event) => {
  const vision = require('@google-cloud/vision');
  const fs = require('fs');
  const client = new vision.ImageAnnotatorClient();
  const request = {
    image: {content: fs.readFileSync('Img/kangaroo2.jpg')},
  };
  const [result] = await client.objectLocalization(request);
  const objects = result.localizedObjectAnnotations;
  console.log(JSON.stringify(objects))
  var objects_detected = locateObject(objects);
  console.log(objects_detected)
  final_direction(objects_detected);
};
exports.handler()


function max_values(left, center, right){ 
  max = 'left';$env:GOOGLE_APPLICATION_CREDENTIALS='level-choir-270012-9c065919be6c.json'
  max_value = left;
  if(right > max_value){
    max = 'right';
    max_value = right;
  }
  if(center > max_value){
    max = 'center';
    max_value = center;
  }
  return max;
}

function get_set_max_value(set_values){
  max = 0;
  for (let value of set_values) {
    if(value > max){
      max = value;
    }
  }
  return max;
}

function locateObject(objects){
  var objects_detected = [];
  if(Object.getOwnPropertyNames(objects).length === 0){
    console.log("Sorry,couldn't detect object");
  }
  else{
    objects.forEach(function(obj){
      if(obj.score > .25) {
        var x_vertices = new Set();
        var y_vertices = new Set();
        var left = 0.0;
        var center = 0.0;
        var right = 0.0;
        obj.boundingPoly.normalizedVertices.forEach(ver => {
          x_vertices.add(Number(ver.x.toFixed(4)));
          y_vertices.add(Number(ver.y.toFixed(4)))
        });
        x_vertices = new Set(Array.from(x_vertices).sort());
        y_vertices = new Set(Array.from(y_vertices).sort());

        var x_iterator = x_vertices.values();
        first_vertex = x_iterator.next().value;
        second_vertex = x_iterator.next().value;

        var object_width = second_vertex - first_vertex;
        if(first_vertex <= 0.3333){
          if(second_vertex < 0.3333){
            left = object_width
          }
          else if(second_vertex < 0.6666){
            left = 0.3333 - first_vertex;
            center = second_vertex - 0.3333;
          }                   
          else if(second_vertex <= 1){
            left = 0.3333 - first_vertex;
            center = 0.3333;
            right = second_vertex - 0.6666;
          }
        }

        if(0.6666 >= first_vertex && first_vertex > 0.3333){
          if(second_vertex < 0.6666) 
            center = object_width;
          else if(second_vertex <= 1){
            center = 0.6666 - first_vertex;
            right = second_vertex - 0.6666;
          }         
        }

        if(first_vertex > 0.6666) 
          right = object_width;

        var moving_direction = "";
        var steps = 0;
        
        if(max_values(left, center, right) === 'right'){
          if(center === 0){
            moving_direction = 'left';
            steps = 0;
          }
          else if(center == 0.3333 && left > 0){
            moving_direction = 'left';
            steps = 2;
          }                
          else{
            moving_direction = 'left';
            steps = 1;
          }
        }

        if(max_values(left, center, right) === 'left'){
          if(center === 0){
            moving_direction = 'right';
            steps = 0;
          }
          if(center === 0.3333 && right > 0){
            moving_direction = 'right';
            steps = 2;
          }  
          else{
            moving_direction = 'right';
            steps = 1;
          }
        }

        if(max_values(left, center, right) === 'center'){
          if(right > left) {
            moving_direction = 'left';
          if(left === 0)
            steps = 1;
          else 
            steps = 2;
          }

          if(left > right) {
            moving_direction = 'right';
            if(right === 0) 
              steps = 1;
            else 
              steps = 2;
          }
        }

        console.log(obj.name, '\n', 'Confidence -', obj.score, '\n', 'Position:',
        max_values(left, center, right), '\n', 'Moving direction -', moving_direction, '\n',
        'Steps -', steps, '\n', )

        var object_details = {
          name : obj.name, 
          position : max_values(left, center, right),
          direction : moving_direction,
          steps : steps,
          left : left,
          right : right,
          center : center
        }
        objects_detected.push(object_details)
      }
    })
  }
  return objects_detected
}

function final_direction(objects_detected){
  console.log(objects_detected.length)
  var output_object = undefined;
  if(objects_detected.length === 0){
    output_object = {
      direction: "",
      steps : 0,
      objects : "Sorry, couldn't detect object"
    };
  }
  else if(objects_detected.length === 1){
    output_object = {
      direction: objects_detected[0].direction,
      steps : objects_detected[0].steps,
      objects : [objects_detected[0].name]
    };
  }
  else{
    var directions = new Set();
    var positions = new Set();
    var moving_steps = new Set();
    var right_values = new Set();
    var left_values = new Set();
    var center_values = new Set();
    var objects = [];
    var final_moving_direction = '';
    var final_steps = '';

    objects_detected.forEach((obj)=>{
      directions.add(obj.direction);
      positions.add(obj.position);
      moving_steps.add(obj.steps);
      left_values.add(obj.left);
      center_values.add(obj.center);
      right_values.add(obj.right);
      objects.push(obj.name);
    });

    max_left_value = get_set_max_value(left_values);
    max_right_value = get_set_max_value(right_values);
    max_moving_steps = get_set_max_value(moving_steps);

    if(positions.size === 3){
      if(max_left_value < max_right_value && max_left_value < 0.1600){
        final_moving_direction = 'left';
        final_steps = '2';
      }
      else if(max_left_value > max_right_value && max_right_value < 0.1600){
        final_moving_direction = 'right';
        final_steps = '2';
      }
      else{
        final_moving_direction = 'Can\'t move, too many objects';
        final_steps = '0';
      }
    }

    else if(directions.size === 1){
      final_moving_direction = Array.from(directions)[0];
      final_steps = max_moving_steps;
    }

    else if(positions.size === 2 && directions.size === 2){
      if(!Array.from(positions).includes('center')){
        if(max_moving_steps>0){
          final_moving_direction = 'Can\'t move, too many objects';
          final_steps = '0';
        }
        else{
          final_moving_direction = 'center';
          final_steps = '0';
        }
      }
      else if(!Array.from(positions).includes('right')){
        final_moving_direction = 'right';
        final_steps = max_moving_steps;
      }
      else{
        final_moving_direction = 'left';
        final_steps = max_moving_steps;
      }
    }

    output_object = {
      direction: final_moving_direction,
      steps : final_steps,
      objects : objects
    };

  }
  console.log(output_object);
}