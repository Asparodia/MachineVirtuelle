let facto n =
  let rec aux n accu =
    if n = 0 then accu
    else aux (n-1) (n*accu)
  in
  aux n 1;;

print_int(facto 17);print_newline()
