
let rec h x = if x > 1 then h (x-1) else x

let g x = h x

let f x = g x;;

print_int(f 234);print_newline();;
