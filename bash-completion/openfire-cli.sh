_openfirecli()
{
  local cur words cword modules commands options
  _init_completion -s || return
  # list for modules
  modules=$(openfire-cli.py --help | sed -n '/^Modules/,/^$/p' | sed -e '1d;$d' | awk '{print $1}' | paste -d' ' -s)
  # list for commands by module
  commands=$(openfire-cli.py ${words[1]} 2>&1 | sed -n '/^Usage/,/^$/p' | sed -e '1d' | awk '{print $3}' | paste -d' ' -s)

  case "${cword}" in
    1)
      # hint module
      COMPREPLY=($(compgen -W "${modules}" -- ${cur})) 
      return 0
      ;;
    2)
      # hint command
      COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
      return 0
      ;;
    *)
      # hint options for command
      options=$(openfire-cli.py ${words[1]} 2>&1 | grep " ${words[2]} " | awk '{$1=$2=$3=""}1' | sed -re 's/<[a-z]+>//g' -e 's/[][()|,.]//g' -e 's/(=)[a-z/]+/\1/g' -e 's/-W//')
      COMPREPLY=( $(compgen -W "${options}" -- ${cur}) )
      [[ $COMPREPLY == *= ]] && compopt -o nospace
      # remove options already specified
      local j k
      for j in ${!COMPREPLY[@]}; do
        # do not touch options which can be specified multiple times
        [[ ${COMPREPLY[j]} == '--group=' ]] && continue
        [[ ${COMPREPLY[j]} == '--broadcast=' ]] && continue
        [[ ${COMPREPLY[j]} == '--owner=' ]] && continue
        [[ ${COMPREPLY[j]} == '--admin=' ]] && continue
        [[ ${COMPREPLY[j]} == '--member=' ]] && continue
        [[ ${COMPREPLY[j]} == '--outcast=' ]] && continue
        # rest of them can be deleted
        for k in ${!words[@]}; do
          [[ ${COMPREPLY[j]} == ${words[k]/=*/=} ]] && unset 'COMPREPLY[j]'
        done
      done
      return 0
      ;;
  esac
} &&
complete -F _openfirecli openfire-cli.py
